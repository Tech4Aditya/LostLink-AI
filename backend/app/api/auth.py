from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import UserCreate, LoginRequest, TokenResponse, UserOut
from ..security import hash_password, verify_password, create_token, current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def normalize_email(value: str) -> str:
    return value.strip().lower()


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    try:
        user = User(email=email, name=payload.name.strip(), password_hash=hash_password(payload.password))
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Account creation failed: {type(exc).__name__}")

    return TokenResponse(access_token=create_token(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    return TokenResponse(access_token=create_token(user))


@router.get("/me", response_model=UserOut)
def me(user=Depends(current_user)):
    return user
