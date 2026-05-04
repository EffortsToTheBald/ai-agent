import logging
from utils.path_tool import get_absolute_path
import os
import datetime 

LOG_PATH = get_absolute_path("logs")

os.makedirs(LOG_PATH, exist_ok=True)

DEFAULT_LOG_FORMAT = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

def get_logger(
        name: str = "agent", 
        console_level: int = logging.INFO, 
        log_file: str = None, 
        file_level: int = logging.DEBUG
        ) -> logging.Logger:
    '''
    get logger instance
    '''
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not log_file:
        log_file = os.path.join(LOG_PATH, f"{name}_{datetime.datetime.now().strftime('%Y-%m-%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    return logger

logger = get_logger()