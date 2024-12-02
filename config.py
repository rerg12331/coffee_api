from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
SECRET = os.environ.get("SECRET")
ALGORITHM = os.environ.get("ALGORITHM")
sender_email = os.environ.get("sender_email")
sender_password = os.environ.get("sender_password")
