import requests
import logging
from datetime import datetime
from ..config.config import load_config

logger = logging.getLogger("clinical_assistant.fhir")
config = load_config()

# Base URL for FHIR server
FHIR_BASE = config["fhir"]["base_url"]


def get_patients():
    """Fetch all patients from FHIR server"""
    try:
        response = requests.get(f"{FHIR_BASE}/Patient")
        response.raise_for_status()
        entries = response.json().get("entry", [])
        return [entry["resource"] for entry in entries]
    except Exception as e:
        logger.error(f"Error fetching patients: {str(e)}")
        return []


def get_patient_data(patient_id, resource_types=["Condition", "Medication", "Procedure"]):
    """Fetch specified resource types for a patient"""
    data = {}
    for resource_type in resource_types:
        try:
            url = f"{FHIR_BASE}/{resource_type}?subject=Patient/{patient_id}"
            response = requests.get(url)
            response.raise_for_status()
            entries = response.json().get("entry", [])
            data[resource_type] = [entry["resource"] for entry in entries]
        except Exception as e:
            logger.error(f"Error fetching {resource_type} for patient {patient_id}: {str(e)}")
            data[resource_type] = []
    return data


def summarize_conditions(patient_id, conditions):
    """Generate a summary of patient conditions"""
    lines = []
    for cond in conditions:
        # Extract condition details
        code = cond.get("code", {}).get("text", "Unnamed condition")
        status = cond.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", "unknown")
        verification = cond.get("verificationStatus", {}).get("coding", [{}])[0].get("code", "unknown")
        onset = cond.get("onsetDateTime", "unknown onset")
        abatement = cond.get("abatementDateTime", None)

        # Format timeline
        if abatement:
            timeline = f"from {onset} to {abatement}"
        else:
            timeline = f"since {onset}"

        lines.append(f"- {code} ({status}, {verification}) {timeline}")

    if not lines:
        return None

    return f"Patient {patient_id} has the following conditions:\n" + "\n".join(lines)


def summarize_medications(patient_id, medications):
    """Generate a summary of patient medications"""
    lines = []
    for med in medications:
        # Extract medication details
        med_name = med.get("medicationCodeableConcept", {}).get("text", "Unnamed medication")
        status = med.get("status", "unknown")

        # Extract timing information
        period_start = med.get("effectivePeriod", {}).get("start", "unknown start")
        period_end = med.get("effectivePeriod", {}).get("end", None)

        # Extract dosage if available
        dosage_info = ""
        if "dosageInstruction" in med and len(med["dosageInstruction"]) > 0:
            dosage = med["dosageInstruction"][0]
            dose_quantity = dosage.get("doseAndRate", [{}])[0].get("doseQuantity", {})
            dose_value = dose_quantity.get("value", "")
            dose_unit = dose_quantity.get("unit", "")

            if dose_value and dose_unit:
                dosage_info = f", {dose_value} {dose_unit}"

            # Add route if available
            route = dosage.get("route", {}).get("text", "")
            if route:
                dosage_info += f" {route}"

        # Format timeline
        if period_end:
            timeline = f"from {period_start} to {period_end}"
        else:
            timeline = f"since {period_start}"

        lines.append(f"- {med_name} ({status}{dosage_info}) {timeline}")

    if not lines:
        return None

    return f"Patient {patient_id} is taking the following medications:\n" + "\n".join(lines)


def summarize_procedures(patient_id, procedures):
    """Generate a summary of patient procedures"""
    lines = []
    for proc in procedures:
        # Extract procedure details
        proc_name = proc.get("code", {}).get("text", "Unnamed procedure")
        status = proc.get("status", "unknown")

        # Extract date information
        performed_date = proc.get("performedDateTime", None)
        performed_period = proc.get("performedPeriod", {})

        if performed_date:
            timeline = f"on {performed_date}"
        elif performed_period:
            start = performed_period.get("start", "unknown start")
            end = performed_period.get("end", None)
            if end:
                timeline = f"from {start} to {end}"
            else:
                timeline = f"since {start}"
        else:
            timeline = "at unknown time"

        # Extract body site if available
        body_site = ""
        if "bodySite" in proc and len(proc["bodySite"]) > 0:
            site = proc["bodySite"][0].get("text", "")
            if site:
                body_site = f" on {site}"

        lines.append(f"- {proc_name} ({status}){body_site} {timeline}")

    if not lines:
        return None

    return f"Patient {patient_id} has undergone the following procedures:\n" + "\n".join(lines)


def process_patients(include_resource_types=["Condition", "Medication", "Procedure"]):
    """Process all patients and generate comprehensive summaries"""
    summaries = []
    failed_patients = []
    patients = get_patients()

    logger.info(f"Processing {len(patients)} patients")

    # Simple progress tracking
    for i, patient in enumerate(patients):
        try:
            pid = patient["id"]

            # Print progress periodically
            if (i + 1) % 10 == 0 or i + 1 == len(patients):
                logger.info(f"Progress: {i + 1}/{len(patients)} patients processed")

            # Get multiple resource types
            data = get_patient_data(pid, resource_types=include_resource_types)

            # Generate different summary types
            condition_summary = summarize_conditions(pid, data.get("Condition", []))
            medication_summary = summarize_medications(pid, data.get("Medication", []))
            procedure_summary = summarize_procedures(pid, data.get("Procedure", []))

            # Combine summaries into a comprehensive patient note
            combined_text = "\n\n".join(filter(None, [
                condition_summary,
                medication_summary,
                procedure_summary
            ]))

            if combined_text:
                summaries.append({
                    "patient_id": pid,
                    "note_text": combined_text,
                    "note_id": f"patient-summary-{pid}",
                    "last_updated": datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Error processing patient {pid}: {str(e)}")
            failed_patients.append({"id": pid, "error": str(e)})

    # Report results
    logger.info(f"Successfully processed {len(summaries)} patients")
    if failed_patients:
        logger.warning(f"Failed to process {len(failed_patients)} patients")

    return summaries, failed_patients