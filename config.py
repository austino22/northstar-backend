# backend/config.py
import os
from datetime import timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def token_expiry() -> timedelta:
  return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
