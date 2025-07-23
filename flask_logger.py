import os
import pathlib
import inspect
import logging
import psutil
import threading
from functools import wraps
from flask import g, has_request_context

# Reference to current file
try:
    FILE = pathlib.Path(__file__)
except NameError:
    FILE = pathlib.Path("logger.py")
BASE = FILE.parent

__all__ = ['logger', 'log_memory_usage', 'log_memory_usage_function']

# Process for memory measurements
_process = psutil.Process(os.getpid())

# -----------------------------
# Custom LogRecord Factory
# -----------------------------
_old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = _old_factory(*args, **kwargs)

    # Flask request context or thread-local worker context
    if has_request_context():
        record.trace_id = getattr(g, 'trace_id', 'no-trace-id')
        record.username = getattr(g, 'username', 'no-username')
        record.client_id = getattr(g, 'client_id', 'no-client-id')
    else:
        worker_ctx = getattr(threading.current_thread(), '_worker_context', {})
        record.trace_id = getattr(worker_ctx, 'trace_id', 'worker_job-1')
        record.username = getattr(worker_ctx, 'username', 'worker_job-1')
        record.client_id = getattr(worker_ctx, 'client_id', 'worker_job-1')

    # Caller info: filename, function name, line number
    try:
        frame = inspect.currentframe()
        while frame:
            frame = frame.f_back
            if not frame:
                break
            fname = frame.f_code.co_filename
            if fname != __file__ and 'logging' not in fname:
                func = frame.f_code.co_name
                lineno = frame.f_lineno
                display = fname.replace('/usr/src/app/', '') if fname.startswith('/usr/src/app/') else fname
                record.func_info = f"{display}:{func}:{lineno}"
                break
        else:
            record.func_info = "unknown:unknown:0"
    except Exception:
        record.func_info = "unknown:unknown:0"

    record.filename = os.path.basename(record.pathname)
    return record

logging.setLogRecordFactory(record_factory)

# -----------------------------
# Memory Usage Filter
# -----------------------------
class MemoryUsageFilter(logging.Filter):
    """
    Logging filter to inject current RSS and VMS (in MB) into each LogRecord.
    """
    def filter(self, record):
        mem = _process.memory_info()
        record.mem_rss = mem.rss / (1024 ** 2)
        record.mem_vms = mem.vms / (1024 ** 2)
        return True

# -----------------------------
# Decorator for Before/After Memory Profiling
# -----------------------------
def log_memory_usage(func):
    """
    Decorator to log memory usage before and after the function execution.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            before = _process.memory_info()
            rss_b = before.rss / (1024 ** 2)
            vms_b = before.vms / (1024 ** 2)
            logger.info(f"[Mem Before] {func.__name__} RSS={rss_b:.2f}MB VMS={vms_b:.2f}MB")

            result = func(*args, **kwargs)

            after = _process.memory_info()
            rss_a = after.rss / (1024 ** 2)
            vms_a = after.vms / (1024 ** 2)
            logger.info(f"[Mem After]  {func.__name__} RSS={rss_a:.2f}MB VMS={vms_a:.2f}MB")
            logger.info(f"[Mem Delta]  {func.__name__} RSS={rss_a - rss_b:+.2f}MB VMS={vms_a - vms_b:+.2f}MB")

            return result
        except Exception as e:
            logger.exception(f"Memory logging failed for {func.__name__}: {e}")
            raise
    return wrapper

# -----------------------------
# Function for Memory Profiling
# -----------------------------
def log_memory_usage_function(tag: str):
    proc = psutil.Process(os.getpid())
    rss = proc.memory_info().rss  / (1024 * 1024)
    vms = proc.memory_info().vms  / (1024 * 1024)
    logger.info(f"{tag} | RSS={rss:.2f}MB VMS={vms:.2f}MB")
    return rss, vms


# -----------------------------
# Logger Configuration
# -----------------------------
# Remove existing root handlers to prevent duplication
root_logger = logging.getLogger()
for h in root_logger.handlers[:]:
    root_logger.removeHandler(h)

# Create application logger
logger = logging.getLogger('app_logger')
logger.setLevel(logging.INFO)
logger.propagate = False

# Remove existing handlers from 'app_logger' to prevent duplicate logs
for h in logger.handlers[:]:
    logger.removeHandler(h)

# Console handler with memory filter
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s+00:00 | [%(trace_id)s] | %(levelname)s | '
    'client_id=%(client_id)s username=%(username)s | %(func_info)s | '
    'RSS=%(mem_rss).2fMB VMS=%(mem_vms).2fMB | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
console_handler.setFormatter(formatter)
console_handler.addFilter(MemoryUsageFilter())
logger.addHandler(console_handler)

# Initialization log
logger.info("✅ Logger initialized successfully with memory profiling")
