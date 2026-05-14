import logging
import sys

logger = logging.getLogger("fastapi_service")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

file_handler = logging.FileHandler("fastapi_logs.log", encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)