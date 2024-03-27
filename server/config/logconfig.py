"""
Project logger config.
"""

import os
import logging

from server.utils.helpers import get_location

LOG_DIR = get_location('../logs')

def init_logger(name):
    global LOG_DIR
    global logger

    # dirs and files
    LOG_FILE = os.path.join(LOG_DIR, f'{name}.log')

    # create dirs
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # get logger by name
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create a file handler
    file_handler = logging.FileHandler(LOG_FILE, mode='a')
    file_handler.setLevel(logging.INFO)

    # create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # create a formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

    # add the formatter to the handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger