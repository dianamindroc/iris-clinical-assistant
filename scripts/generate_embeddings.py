import os
import sys
import logging
import json

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.functions.embedding import generate_embedding
from app.functions.iris import store_embedded_notes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("clinical_assistant.generate_embeddings")


def main():
    """Generate embeddings for patient summaries and store in IRIS"""
    logger.info("Starting embedding generation process")

    # Load patient summaries
    try:
        with open("patient_summaries.json", "r") as f:
            summaries = json.load(f)
    except FileNotFoundError:
        logger.error("patient_summaries.json not found. Run fetch_fhir_data.py first.")
        return

    logger.info(f"Loaded {len(summaries)} patient summaries")

    # Generate embeddings
    logger.info("Generating embeddings...")
    embeddings = []
    for i, summary in enumerate(summaries):
        if (i + 1) % 10 == 0 or i + 1 == len(summaries):
            logger.info(f"Generated {i + 1}/{len(summaries)} embeddings")

        embedding = generate_embedding(summary["note_text"])
        embeddings.append(embedding)

    # Store in IRIS
    logger.info("Storing embeddings in IRIS...")
    inserted, updated = store_embedded_notes(summaries, embeddings)

    logger.info(f"Completed: {inserted} notes inserted, {updated} notes updated")


if __name__ == "__main__":
    main()