__author__ = 'jaya'

# External import
import logging

def create_logger(name, level=logging.DEBUG):
    # Create custom logger
    logger = logging.getLogger(name)
    # Create handler
    console_handler = logging.StreamHandler()
    # Create custom formatter
    console_format = logging.Formatter('Time: %(asctime)s, %(levelname)s: %(name)s: %(funcName)s: Line No: %(lineno)d, Message: %(message)s ')
    # Add format to handle
    console_handler.setFormatter(console_format)
    # Add handlers to logger
    logger.addHandler(console_handler)
    # Set level to logger
    logger.setLevel(level)
    return logger