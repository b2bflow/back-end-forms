import os
import logging
from logging.handlers import RotatingFileHandler


def get_logger():
    """
    Configures and returns a logger with both console and rotating file handlers.

    The logger is set to the DEBUG level and logs messages in the format:
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s". It creates a "logs"
    directory if it does not exist and logs to "logs/app.log" with a maximum file
    size of 5MB and keeps up to 5 backup files.

    Returns:
        logging.Logger: Configured logger instance.
    """

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


logger = get_logger()