from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


# ── Password strength validator ────────────────────────

def _validate_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", v):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", v):
        raise ValueError("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
        raise ValueError("Password must contain at least one special character")
    common = {
        "password", "password123", "admin123", "12345678", "qwerty",
        "abc123", "letmein", "welcome", "monkey", "dragon",
        "master", "sunshine", "iloveyou", "admin", "root",
    }
    if v.lower() in common:
        raise ValueError("Password is too common. Please choose a stronger password.")
    return v


# ── Auth request models ────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """Sign-up payload: email, display name, and a strong password (≥ 8 chars)."""

    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password(v)

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password_strength(cls, v: str) -> str:
        return _validate_password(v)


    @field_validator("confirm_password")
    @classmethod
    def validate_passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z\s\-\'\.]+$", v):
            raise ValueError(
                "Name may only contain letters, spaces, hyphens, apostrophes, and periods"
            )
        return v.strip()



class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SetSessionCookieRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
