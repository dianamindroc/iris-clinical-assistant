import intersystems_iris.dbapi._DBAPI as iris
import json
import logging
from ..config.config import load_config

logger = logging.getLogger("clinical_assistant.iris")
config = load_config()


def get_iris_connection():
    """Get connection to IRIS database"""
    try:
        conn = iris.connect(
            hostname=config["iris"]["hostname"],
            port=config["iris"]["port"],
            namespace=config["iris"]["namespace"],
            username=config["iris"]["username"],
            password=config["iris"]["password"]
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to IRIS: {str(e)}")
        raise


def fetch_notes():
    """Retrieve all embedded notes from IRIS"""
    try:
        conn = get_iris_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT PatientID, NoteID, NoteText, Embedding FROM NoteEmbeddings")

        results = []
        for row in cursor.fetchall():
            embedding = json.loads(row[3])
            results.append({
                "patient_id": row[0],
                "note_id": row[1],
                "text": row[2],
                "embedding": embedding
            })

        cursor.close()
        conn.close()

        logger.info(f"Retrieved {len(results)} notes from IRIS")
        return results
    except Exception as e:
        logger.error(f"Error fetching notes: {str(e)}")
        return []


def store_embedded_notes(summaries, embeddings):
    """Store embedded notes in IRIS database"""
    try:
        conn = get_iris_connection()
        cursor = conn.cursor()

        # Ensure table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS NoteEmbeddings (
            ID SERIAL,
            PatientID VARCHAR(64),
            NoteID VARCHAR(64),
            NoteText TEXT,
            Embedding TEXT
        )
        """)

        # Get existing notes to handle updates
        cursor.execute("SELECT NoteID FROM NoteEmbeddings")
        existing_notes = {row[0]: True for row in cursor.fetchall()}

        inserted = 0
        updated = 0

        for i, summary in enumerate(summaries):
            embedding_json = json.dumps(embeddings[i])

            # Check if note already exists
            if summary["note_id"] in existing_notes:
                cursor.execute("""
                    UPDATE NoteEmbeddings 
                    SET NoteText = ?, Embedding = ?
                    WHERE NoteID = ?
                """, (
                    summary["note_text"],
                    embedding_json,
                    summary["note_id"]
                ))
                updated += 1
            else:
                cursor.execute("""
                    INSERT INTO NoteEmbeddings 
                    (PatientID, NoteID, NoteText, Embedding)
                    VALUES (?, ?, ?, ?)
                """, (
                    summary["patient_id"],
                    summary["note_id"],
                    summary["note_text"],
                    embedding_json
                ))
                inserted += 1

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Database updated: {inserted} inserted, {updated} updated")
        return inserted, updated
    except Exception as e:
        logger.error(f"Error storing notes: {str(e)}")
        raise


def get_patient_list():
    """Retrieve list of available patients from IRIS database"""
    try:
        conn = get_iris_connection()
        cursor = conn.cursor()

        # Query for distinct patient IDs
        cursor.execute("SELECT DISTINCT PatientID FROM NoteEmbeddings ORDER BY PatientID")

        # Get the results
        patients = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return patients
    except Exception as e:
        logger.error(f"Error fetching patient list: {str(e)}")
        return []