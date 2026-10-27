from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


# ── Password strength validator ────────────────────────

def _validate_password(v: str) -> str:
    if len(v) < 12:
        raise ValueError("Password must be at least 12 characters long")
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
    """Sign-up payload: email, display name, and a strong password (≥ 12 chars)."""

    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password(v)

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


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., min_length=1)


class PasswordResetRequest(BaseModel):
    email: EmailStr



class PasswordResetConfirm(BaseModel):
    """Step 2 of password reset – supply the reset token and the new password."""

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=12, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return _validate_password(v)



class ChangePasswordRequest(BaseModel):
    """Authenticated user changing their own password."""

    current_password: str
    new_password: str = Field(..., min_length=12, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return _validate_password(v)
    
    

class ReauthRequest(BaseModel):
    """Re-authentication gate before sensitive actions.

    Either *password* or *mfa_code* must be supplied.
    """

    password: Optional[str] = None
    mfa_code: Optional[str] = None

    @field_validator("mfa_code")
    @classmethod
    def validate_either_provided(cls, v: Optional[str], info) -> Optional[str]:
        if not v and not info.data.get("password"):
            raise ValueError("Either password or mfa_code must be provided")
        return v
