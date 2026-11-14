"""Shared MySQL connection helper for the notebooks and the Streamlit app.

Credentials are read from the .env file in this folder (never hard-coded).
"""
import os
from pathlib import Path

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine

ENV_FILE = Path(__file__).resolve().parent / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)
except ImportError:
    # python-dotenv is not installed in this kernel -> read the simple KEY=VALUE lines ourselves
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

DB_NAME = os.getenv("MYSQL_DB", "tmdb")


def get_engine(with_database: bool = True) -> Engine:
    """Return a SQLAlchemy engine for MySQL (via PyMySQL).

    with_database=False connects to the server only - used once to CREATE DATABASE.
    URL.create() safely handles special characters such as '@' in the password.
    """
    url = URL.create(
        "mysql+pymysql",
        username=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=DB_NAME if with_database else None,
        query={"charset": "utf8mb4"},
    )
    return create_engine(url, pool_pre_ping=True)
