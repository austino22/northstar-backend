# backend/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class GoalCreate(BaseModel):
    name: str
    target_amount: float
    target_date: str
    current_amount: float = 0.0

class GoalOut(BaseModel):
    id: int
    name: str
    target_amount: float
    target_date: str
    current_amount: float
    class Config:
        orm_mode = True

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[str] = None
    current_amount: Optional[float] = None
