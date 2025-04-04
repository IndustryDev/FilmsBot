import logging.config
import os.path
import sys
from logging import handlers

LOG_FILE = os.path.join(os.getcwd(), 'bot.log')

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        handlers.RotatingFileHandler(LOG_FILE, mode='a', encoding='utf-8', maxBytes=10485760, backupCount=5),
    ]
)

logger = logging.getLogger(__name__)

