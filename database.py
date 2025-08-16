# backend/database.py
import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read DATABASE_URL from environment; fall back to local SQLite for dev
raw_url = os.getenv("DATABASE_URL", "sqlite:///./northstar.db")

# If it's Postgres without an explicit driver, switch to psycopg (v3)
if raw_url.startswith("postgresql://"):
    DATABASE_URL = raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    DATABASE_URL = raw_url

# Ensure SSL is required for managed Postgres providers (e.g., Neon)
if DATABASE_URL.startswith("postgresql+psycopg://"):
    parsed = urlparse(DATABASE_URL)
    q = dict(parse_qsl(parsed.query))
    if "sslmode" not in q:
        q["sslmode"] = "require"
        parsed = parsed._replace(query=urlencode(q))
        DATABASE_URL = urlunparse(parsed)

# Only SQLite needs check_same_thread
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # helps avoid stale connections on long-lived services
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI dependency for DB sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
