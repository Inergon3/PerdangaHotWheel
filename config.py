import os

from dotenv import load_dotenv

load_dotenv()
host = os.getenv("host")
user = os.getenv("user")
password_bd = os.getenv("password_bd")
db_name = os.getenv("db_name")
steam_api_key = os.getenv("steam_api_key")
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
