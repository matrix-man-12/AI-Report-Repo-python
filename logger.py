import logging
import os
from datetime import datetime
import config

def setup_logging():
    os.makedirs(config.LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(config.LOG_DIR, f"execution_{timestamp}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # To avoid duplicate handlers if setup_logging is called multiple times
    if logger.handlers:
        return logger

    # File handler: receives DEBUG and above (Detailed stack traces, inputs, etc.)
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')
    fh.setFormatter(file_formatter)

    # Console handler: receives INFO and above (Clean, friendly messages)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    ch.setFormatter(console_formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

# Initialize the config on import
setup_logging()
