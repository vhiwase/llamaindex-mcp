import pathlib
import os
import logging
import uuid
import inspect
from flask import Flask, g, has_request_context, request

# adding repo folder in system for file imports
try:
    FILE = pathlib.Path(__file__)
except NameError:
    FILE = pathlib.Path("logger.py")
BASE = FILE.parent

__all__ = ['logger']

# Create a custom log record factory to include trace_id and caller information
old_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    
    # Add trace_id
    if has_request_context():
        record.trace_id = getattr(g, 'trace_id', 'no-trace-id')
        record.username = getattr(g, 'username', 'no-username')
        record.client_id = getattr(g, 'client_id', 'no-client-id')
    else:
        # Try to get from thread-local worker context if available
        import threading
        worker_context = getattr(threading.current_thread(), '_worker_context', None)
        if worker_context:
            record.trace_id = getattr(worker_context, 'trace_id', 'worker_job-1')
            record.username = getattr(worker_context, 'username', 'worker_job-1')
            record.client_id = getattr(worker_context, 'client_id', 'worker_job-1')
        else:
            record.trace_id = 'worker_job-1'
            record.username = 'worker_job-1'
            record.client_id = 'worker_job-1'
    
    # Get caller function name and file path without /usr/src/app/ prefix
    try:
        # Go back in the stack to find the actual caller
        frame = inspect.currentframe()
        # Skip this frame and logging internals
        while frame:
            if frame.f_code.co_filename != __file__ and not frame.f_code.co_filename.endswith('logging/__init__.py'):
                break
            frame = frame.f_back
            
        if frame:
            func_name = frame.f_code.co_name
            file_path = frame.f_code.co_filename
            line_number = frame.f_lineno
            # Remove /usr/src/app/ prefix from file path
            if file_path.startswith('/usr/src/app/'):
                file_path = file_path[len('/usr/src/app/'):]
            record.func_info = f"{file_path}:{func_name}:{line_number}"
        else:
            record.func_info = "unknown_file:unknown_function:0"
    except Exception:
        record.func_info = "unknown_file:unknown_function:0"
    
    # Keep the filename for backward compatibility
    record.filename = os.path.basename(record.pathname)
    
    return record

logging.setLogRecordFactory(record_factory)

# Disable any existing loggers to prevent conflicts with logging.conf
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Define logger configuration with the required format
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s+00:00 | [%(trace_id)s] | %(levelname)s | client_id=%(client_id)s username=%(username)s | %(func_info)s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
))

# Get root logger and add handler
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Test that logger is working
logger.info("Logger initialized successfully")