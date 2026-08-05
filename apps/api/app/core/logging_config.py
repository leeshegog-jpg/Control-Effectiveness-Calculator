"""R0 scaffold placeholder -- structured logging configuration.
Wired at app startup (app/main.py). No log handlers configured beyond
stdlib defaults yet.
"""

import logging


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO)
