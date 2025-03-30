import os
import sys
import logging

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.functions.iris import get_iris_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("clinical_assistant.setup_database")


def setup_tables():
    """Set up necessary database tables in IRIS"""
    logger.info("Setting up database tables in IRIS")

    try:
        conn = get_iris_connection()
        cursor = conn.cursor()

        # Create NoteEmbeddings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS NoteEmbeddings (
            ID SERIAL,
            PatientID VARCHAR(64),
            NoteID VARCHAR(64),
            NoteText TEXT,
            Embedding TEXT
        )
        """)

        # Create index on NoteID for faster lookups
        try:
            cursor.execute("CREATE INDEX idx_noteembeddings_noteid ON NoteEmbeddings (NoteID)")
            logger.info("Created index on NoteID")
        except Exception as e:
            logger.warning(f"Index creation failed (may already exist): {str(e)}")

        # Create index on PatientID
        try:
            cursor.execute("CREATE INDEX idx_noteembeddings_patientid ON NoteEmbeddings (PatientID)")
            logger.info("Created index on PatientID")
        except Exception as e:
            logger.warning(f"Index creation failed (may already exist): {str(e)}")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("Database setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        return False


if __name__ == "__main__":
    setup_tables()