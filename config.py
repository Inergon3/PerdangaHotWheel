import os

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "db_name": os.getenv("POSTGRES_DB"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}

APP_CONFIG = {
    "steam_api_key": os.getenv("STEAM_API_KEY"),
    "secret_key": os.getenv("SECRET_KEY"),
    "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256")
}

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db_name']}"
)
