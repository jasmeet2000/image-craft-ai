"""Root wrapper for Hugging Face Spaces deployment."""
import logging

from src.ui.app import create_app
from src.config.settings import get_settings
from src.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)

# Initialize logging before creating the app
settings = get_settings()
setup_logging(settings.log_dir, settings.log_level)

# Hugging Face Spaces automatically looks for an object named `demo` or `app` 
# in the root `app.py` file to serve.
demo = create_app()
demo.queue()

if __name__ == "__main__":
    logger.info("Starting Image Craft AI for Hugging Face Spaces...")
    # HF Spaces handles the port and server name automatically.
    demo.launch()
