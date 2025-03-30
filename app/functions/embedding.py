from sentence_transformers import SentenceTransformer
import logging
from functools import lru_cache
from ..config.config import load_config
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*NumPy: _ARRAY_API not found.*")

logger = logging.getLogger("clinical_assistant.embedding")
config = load_config()

@lru_cache(maxsize=1)
def get_embedding_model():
    """Load and cache the embedding model"""
    model_name = config["embedding"]["model"]
    logger.info(f"Loading embedding model: {model_name}")
    return SentenceTransformer(model_name)

def generate_embedding(text):
    """Generate embedding vector for a text"""
    try:
        model = get_embedding_model()
        embedding = model.encode(text, convert_to_tensor=True).tolist()
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise