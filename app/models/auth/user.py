from __future__ import annotations
from typing import List
from pydantic import BaseModel, EmailStr, Field


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    roles: List[str] = Field(default_factory=list)
    email_verified: bool
    has_password: bool
    totp_enabled: bool
    email_mfa_enabled: bool
    recovery_codes_available: bool
