import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# Env variables
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
SERVER_PORT = os.getenv("SERVER_PORT")

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")

POSTGRESQL_URL = (
    f"postgresql+asyncpg://"
    f"{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}"
    f"/{POSTGRES_DATABASE}"
)

# TIME GAP AFTER REPR IS COUNTED AS BEING GONE FROM THE MEET
TIME_GAP = timedelta(hours=3)

# TIME AFTER WHICH REPR IS FREED FROM THE WORK TODAY
TIME_FREED = timedelta(hours=5)
