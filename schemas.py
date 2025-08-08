from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# -------- users --------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None

# -------- goals --------
class GoalBase(BaseModel):
    name: str
    target_amount: float
    target_date: str
    current_amount: float

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[str] = None
    current_amount: Optional[float] = None

class GoalOut(GoalBase):
    id: int
    class Config:
        from_attributes = True
