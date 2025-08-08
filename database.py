from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# For dev: SQLite file. For prod: use PostgreSQL DSN.
SQLALCHEMY_DATABASE_URL = "sqlite:///./northstar.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # only for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
