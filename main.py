# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User, Goal
from schemas import (
    UserCreate,
    UserOut,
    Token,
    GoalCreate,
    GoalOut,
    GoalUpdate,
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

# Create tables at startup (dev convenience; for prod use migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NorthStar API", version="0.3.0")

# CORS: allow local dev + (later) your deployed frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://northstar-frontend-kohl.vercel.app",
    # "https://your-frontend.vercel.app",
    # And your custom domain when ready:
    # "https://app.yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health check ---
@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
#         AUTH
# =========================

@app.post("/auth/register", response_model=UserOut, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=user_in.email, password_hash=hash_password(user_in.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm sends "username" as the identifier (we use email there)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = create_access_token(subject=user.email)
    return Token(access_token=access)


@app.get("/auth/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

# =========================
#         GOALS
# =========================

@app.get("/goals", response_model=list[GoalOut])
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .order_by(Goal.id.desc())
        .all()
    )
    return rows


@app.post("/goals", response_model=GoalOut, status_code=201)
def create_goal(
    goal_in: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    g = Goal(
        user_id=current_user.id,
        name=goal_in.name,
        target_amount=goal_in.target_amount,
        target_date=goal_in.target_date,
        current_amount=goal_in.current_amount,
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@app.put("/goals/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: int,
    updates: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    g = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Goal not found")

    if updates.name is not None:
        g.name = updates.name
    if updates.target_amount is not None:
        g.target_amount = updates.target_amount
    if updates.target_date is not None:
        g.target_date = updates.target_date
    if updates.current_amount is not None:
        g.current_amount = updates.current_amount

    db.commit()
    db.refresh(g)
    return g


@app.delete("/goals/{goal_id}", response_model=GoalOut)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    g = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(g)
    db.commit()
    return g
