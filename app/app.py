import os
import sys
import logging
from flask import Flask
from app.api.routes import setup_routes
from app.config.config import load_config
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*NumPy: _ARRAY_API not found.*")



# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("clinical_assistant.log"), logging.StreamHandler()]
)
logger = logging.getLogger("clinical_assistant")

# Create and configure Flask app
app = Flask(__name__)
config = load_config()

# Setup routes
setup_routes(app)


def create_template_dir():
    """Make sure templates directory exists"""
    os.makedirs('templates', exist_ok=True)


if __name__ == "__main__":
    # Create templates directory
    create_template_dir()

    # Check if running in CLI mode
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        from cli import cli_interface

        cli_interface()
    else:
        # Run in web mode
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"Starting web server at http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)