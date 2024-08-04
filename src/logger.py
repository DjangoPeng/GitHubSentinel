# src/logger.py
from loguru import logger
import sys

# Configure Loguru
logger.remove()  # Remove the default logger
logger.add(sys.stdout, level="DEBUG", format="{time} {level} {message}", colorize=True)
logger.add("logs/app.log", rotation="1 MB", level="DEBUG")

# Alias the logger for easier import
LOG = logger

# Make the logger available for import with the alias
__all__ = ["LOG"]
