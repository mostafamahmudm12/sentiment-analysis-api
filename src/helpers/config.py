import os
from dotenv import load_dotenv

# Load .env file
load_dotenv(override=True)

APP_NAME = os.getenv("APP_NAME")
VERSION = os.getenv("VERSION")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")


# SRC Folder path
SRC_FOLDER_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_PATH = os.path.join(SRC_FOLDER_PATH, "assets", "storage")
os.makedirs(STORAGE_PATH, exist_ok=True)