import os
import sys
import logging

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.functions.fhir import process_patients
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("clinical_assistant.fetch_fhir")


def main():
    """Fetch FHIR data and generate patient summaries"""
    logger.info("Starting FHIR data fetch process")

    # Process patients with all resource types
    summaries, failed_patients = process_patients(
        include_resource_types=["Condition", "Medication", "Procedure"]
    )

    # Save summaries to file for later use
    with open("patient_summaries.json", "w") as f:
        json.dump(summaries, f, indent=2)

    logger.info(f"Saved {len(summaries)} patient summaries to patient_summaries.json")

    if failed_patients:
        logger.warning(f"Failed to process {len(failed_patients)} patients")
        logger.warning(f"First few failures: {failed_patients[:3]}")

    return summaries


if __name__ == "__main__":
    main()