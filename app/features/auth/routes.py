from fastapi import APIRouter, Request, Depends

from models.auth.auth import LoginRequest, RegisterRequest
from models.auth.mfa import TotpEnableRequest, DisableMfaRequest, MfaVerifyRequest
from features.auth.v1.authentication import login_api, signup_api
from features.auth.v1.two_factor import disable_2fa_api, enable_2fa_api, setup_2fa_api, verify_2fa_api
from features.auth.v1.auth.logout import logout_api
from features.auth.v1.oauth_apis import oauth_login_api, oauth_callback_api
from middlewares.limiter import limiter
from utils.get_current_user import get_current_user
from utils.core_response import core_response

router = APIRouter()


@router.post("/login")
@limiter.limit("30/minute")
async def auth(request: Request, payload: LoginRequest):
    return await login_api(payload)


@router.post("/signup")
@limiter.limit("30/minute")
async def signup_route(request: Request, payload: RegisterRequest):
    return await signup_api(payload)


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return await core_response(
        status_code=200,
        message="Current user info",
        data=current_user
    )


@router.post("/logout")
@limiter.limit("30/minute")
async def logout(request: Request, current_user: dict = Depends(get_current_user)):
    return await logout_api(request)



@router.post("/2fa/setup")
@limiter.limit("10/minute")
async def setup_2fa(request: Request, current_user: dict = Depends(get_current_user)):
    return await setup_2fa_api(current_user["id"], current_user["email"])


@router.post("/2fa/enable")
@limiter.limit("10/minute")
async def enable_2fa(request: Request, payload: TotpEnableRequest, current_user: dict = Depends(get_current_user)):
    return await enable_2fa_api(current_user["id"], payload.code)


@router.post("/2fa/disable")
@limiter.limit("10/minute")
async def disable_2fa(request: Request, payload: DisableMfaRequest, current_user: dict = Depends(get_current_user)):
    return await disable_2fa_api(current_user["id"], None, payload.code)


@router.post("/2fa/verify")
@limiter.limit("10/minute")
async def verify_2fa(request: Request, payload: MfaVerifyRequest):
    temp_token = request.headers.get("X-2FA-Token")
    if not temp_token:
        return await core_response(
            status_code=400,
            message="Temporary token required"
        )
    return await verify_2fa_api(temp_token, payload.code)


@router.get("/oauth/{provider}")
@limiter.limit("30/minute")
async def oauth_login(provider: str, request: Request):
    return await oauth_login_api(provider, request)


@router.get("/oauth/{provider}/callback")
@limiter.limit("30/minute")
async def oauth_callback(provider: str, request: Request):
    return await oauth_callback_api(provider, request)
