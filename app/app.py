import os
import sys
import logging
from flask import Flask

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("clinical_assistant.log"), logging.StreamHandler()]
)
logger = logging.getLogger("clinical_assistant")

# Initialize Flask app
app = Flask(__name__)


def check_db_initialized():
    """Check if the database is initialized"""
    from app.functions.iris import get_iris_connection
    try:
        conn = get_iris_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM NoteEmbeddings")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0
    except Exception:
        return False


def initialize_database(force=False):
    """Initialize database and load data if needed"""
    if force or not check_db_initialized():
        logger.info("Database not initialized or force flag set. Setting up database...")

        # Step 1: Setup database tables
        logger.info("Step 1/3: Setting up database tables")
        from scripts.setup_database import setup_tables
        setup_tables()

        # Step 2: Fetch FHIR data
        logger.info("Step 2/3: Fetching FHIR data (this may take a few minutes)")
        from scripts.fetch_fhir_data import main as fetch_fhir
        fetch_fhir()

        # Step 3: Generate embeddings
        logger.info("Step 3/3: Generating embeddings (this may take a few minutes)")
        from scripts.generate_embeddings import main as generate_embeddings
        generate_embeddings()

        logger.info("Database initialization complete!")
        return True
    else:
        logger.info("Database already initialized, skipping setup")
        return False


def setup_app():
    """Setup Flask application and routes"""
    from app.api.routes import setup_routes
    from app.config.config import load_config

    config = load_config()
    setup_routes(app)

    return app


def create_template_dir():
    """Make sure templates directory exists"""
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)


if __name__ == "__main__":
    # Create templates directory
    create_template_dir()

    # Check for initialization flag
    skip_init = "--skip-init" in sys.argv
    force_init = "--force-init" in sys.argv

    # Initialize database if needed
    if not skip_init:
        initialize_database(force=force_init)

    # Setup Flask app
    app = setup_app()

    # Check if running in CLI mode
    if "--cli" in sys.argv:
        from app.cli import cli_interface

        cli_interface()
    else:
        # Run in web mode
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"Starting web server at http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)