import logging
from logging.handlers import RotatingFileHandler
import os

def setup_app_logger(app):
    os.makedirs("logs", exist_ok=True)

    handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10_000_000,
        backupCount=3
    )

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s"
    )

    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
