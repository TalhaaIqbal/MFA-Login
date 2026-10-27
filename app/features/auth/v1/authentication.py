# Path: features/auth/v1/auth.py
from .auth.login import login
from .auth.signup import signup
from models.auth.auth import LoginRequest, RegisterRequest


async def login_api(payload: LoginRequest):
    return await login(payload)


async def signup_api(payload: RegisterRequest):
    return await signup(payload)


__all__ = ['login_api', 'signup_api']
