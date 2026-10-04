from fastapi import APIRouter, HTTPException, status, Depends
import re
from pydantic import BaseModel, EmailStr, Field, field_validator

from auth.security import hash_password, verify_password, create_access_token
from auth.deps import get_current_user
from database.db import create_user, get_user_by_email

router = APIRouter()


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        problems = []
        if not re.search(r"[A-Z]", v):
            problems.append("an uppercase letter")
        if not re.search(r"[a-z]", v):
            problems.append("a lowercase letter")
        if not re.search(r"[0-9]", v):
            problems.append("a number")
        if not re.search(r"[^A-Za-z0-9]", v):
            problems.append("a symbol")
        if problems:
            raise ValueError("Password must contain " + ", ".join(problems))
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/signup", response_model=AuthResponse)
def signup(data: SignupRequest):
    existing = get_user_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    hashed = hash_password(data.password)
    user_id = create_user(data.name, data.email, hashed)

    token = create_access_token({"sub": str(user_id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "name": data.name, "email": data.email}
    }


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest):
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = create_access_token({"sub": str(user["id"])})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
    }


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"]
    }
