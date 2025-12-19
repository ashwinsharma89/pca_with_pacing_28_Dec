import reflex as rx
import sys
import os
from pathlib import Path

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = str(Path(current_dir).parent.parent.parent.resolve())

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.frontend_logger import logger

class BaseState(rx.State):
    """Base state for the application."""
    
    def log(self, message: str, level: str = "info"):
        """Log a message from the frontend state."""
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        elif level == "debug":
            logger.debug(message)
        else:
            logger.info(message)
