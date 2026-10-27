from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


MfaMethod = Literal["totp", "email", "recovery"]


class MfaVerifyRequest(BaseModel):
    method: Optional[MfaMethod] = None
    code: str = Field(..., min_length=1, max_length=64)


class TotpEnableRequest(BaseModel):
    """Confirm TOTP setup by supplying the 6-digit code from the authenticator app."""

    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    challenge_id: Optional[str] = None


class EmailOtpEnableRequest(BaseModel):
    """Confirm email OTP setup by supplying the 6-digit code sent to email."""

    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    challenge_id: Optional[str] = None


class DisableMfaRequest(BaseModel):
    """Turn off a specific MFA factor.

    *code* must be a valid credential for the factor being disabled (e.g. a TOTP
    code when disabling TOTP, or an email OTP when disabling email MFA).
    """

    method: MfaMethod
    code: str = Field(..., min_length=1, max_length=64)


class DisableEmailOtpRequest(BaseModel):
    """Turn off email OTP 2FA with password authentication."""

    password: str = Field(..., min_length=1)


class EmailOtpVerifyRequest(BaseModel):
    """Verify email OTP during login."""

    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
