import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger("clinical_assistant.config")


def load_config():
    """Load configuration from environment variables"""
    # Load environment variables from .env file
    load_dotenv()

    config = {
        "iris": {
            "hostname": os.environ.get("IRIS_HOST", "localhost"),
            "port": int(os.environ.get("IRIS_PORT", 1972)),
            "namespace": os.environ.get("IRIS_NAMESPACE", "USER"),
            "username": os.environ.get("IRIS_USERNAME", "admin"),
            "password": os.environ.get("IRIS_PASSWORD", "supersecret")
        },
        "embedding": {
            "model": os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        },
        "llm": {
            "api_key": os.environ.get("HF_API_KEY", ""),
            "model": os.environ.get("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct"),
            "max_length": int(os.environ.get("LLM_MAX_LENGTH", 256)),
            "temperature": float(os.environ.get("LLM_TEMPERATURE", 0.7)),
            "top_p": float(os.environ.get("LLM_TOP_P", 0.9))
        },
        "fhir": {
            "base_url": os.environ.get("FHIR_BASE_URL", "http://localhost:52773/fhir/r4")
        }
    }

    logger.info("Configuration loaded")
    return config