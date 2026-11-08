
from pathlib import Path

# Project configuration
BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "connectx.db"

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

APP_NAME = "ConnectX"
APP_VERSION = "1.0.0"

MAX_MESSAGE_LENGTH = 2000
HISTORY_LIMIT = 50
