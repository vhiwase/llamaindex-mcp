import os
import multiprocessing
import sys
import pathlib

try:
    FILE = pathlib.Path(__file__)
except NameError:
    FILE = pathlib.Path("tm_config.py")
BASE = FILE.parent
BASE_ABSOLUTE = BASE.absolute()
BASE_ABSOLUTE = BASE_ABSOLUTE.parent.parent
if BASE_ABSOLUTE.absolute().as_posix() not in sys.path:
    sys.path.append(BASE_ABSOLUTE.absolute().as_posix())

from config.aws_secrets import AWSSecretsManager

from dotenv import load_dotenv
load_dotenv()

__all__ = [
    "DevConfig",
    "QAConfig",
    "StageConfig",
    "ProdConfig",
    "ProdGovCloudConfig",
    "PreProdGovCloudConfig",
    "LocalConfig"
]

class BaseConfig(object):
    """Base configuration."""

    OCR_ENV = ""
    
    # Set environment variables from AWS Secrets Manager
    secrets_manager = AWSSecretsManager()
    secrets_manager.set_environment_variables()

     # GPT-4o configuration for multimodal detection
    AZURE_GPT4o_OPENAI_API_KEY = os.getenv("AZURE_GPT4o_OPENAI_API_KEY")
    AZURE_GPT4o_OPENAI_API_TYPE = os.getenv("AZURE_GPT4o_OPENAI_API_TYPE", "azure")
    AZURE_GPT4o_OPENAI_API_VERSION = os.getenv("AZURE_GPT4o_OPENAI_API_VERSION")
    AZURE_GPT4o_OPENAI_DEPLOYMENT = os.getenv("AZURE_GPT4o_OPENAI_DEPLOYMENT")
    AZURE_GPT4o_OPENAI_ENDPOINT = os.getenv("AZURE_GPT4o_OPENAI_ENDPOINT")
    AZURE_GPT4o_OPENAI_MODEL_VERSION = os.getenv("AZURE_GPT4o_OPENAI_MODEL_VERSION")

class DevConfig(BaseConfig):
    """Dev configuration."""

    OCR_ENV = "dev"

class QAConfig(BaseConfig):
    """QA configuration."""

    OCR_ENV = "qa"

class LocalConfig(DevConfig):
    """Local Development configuration."""

    OCR_ENV = "local"
    
class StageConfig(BaseConfig):
    """Stage configuration."""

    OCR_ENV = "stage"

class ProdConfig(BaseConfig):
    """Prod configuration."""

    OCR_ENV = "prod"

class ProdGovCloudConfig(BaseConfig):
    """Prod configuration for GovCloud."""

    OCR_ENV = "prod"

class PreProdGovCloudConfig(BaseConfig):
    """PreProd configuration for GovCloud."""

    OCR_ENV = "preprod"
