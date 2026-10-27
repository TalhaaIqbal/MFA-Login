from fastapi import APIRouter, Request, Depends, Response

from models.auth.auth import LoginRequest, RegisterRequest, SetSessionCookieRequest
from models.auth.mfa import TotpEnableRequest, DisableMfaRequest, MfaVerifyRequest, EmailOtpEnableRequest, DisableEmailOtpRequest, EmailOtpVerifyRequest
from features.auth.v1.authentication import login_api, signup_api
from features.auth.v1.two_factor import disable_2fa_api, enable_2fa_api, setup_2fa_api, verify_2fa_api
from features.auth.v1.auth.logout import logout_api
from features.auth.v1.oauth_apis import oauth_login_api, oauth_callback_api
from features.auth.v1.email_otp_apis import setup_email_otp_api, enable_email_otp_api, disable_email_otp_api, verify_email_otp_api
from middlewares.limiter import limiter
from utils.get_current_user import get_current_user
from utils.core_response import core_response
from logging_config import logger

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
    logger.info(f"enable_2fa route called - user_id: {current_user['id']}, code: {payload.code}, challenge_id: {payload.challenge_id}")
    return await enable_2fa_api(current_user["id"], payload.code, payload.challenge_id)


@router.post("/2fa/disable")
@limiter.limit("10/minute")
async def disable_2fa(request: Request, payload: DisableMfaRequest, current_user: dict = Depends(get_current_user)):
    return await disable_2fa_api(current_user["id"], payload.password, payload.totp_code)


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


@router.post("/email-otp/setup")
@limiter.limit("10/minute")
async def setup_email_otp(request: Request, current_user: dict = Depends(get_current_user)):
    return await setup_email_otp_api(current_user["id"], current_user["email"])


@router.post("/email-otp/enable")
@limiter.limit("10/minute")
async def enable_email_otp(request: Request, payload: EmailOtpEnableRequest, current_user: dict = Depends(get_current_user)):
    return await enable_email_otp_api(current_user["id"], payload.code, payload.challenge_id)


@router.post("/email-otp/disable")
@limiter.limit("10/minute")
async def disable_email_otp(request: Request, payload: DisableEmailOtpRequest, current_user: dict = Depends(get_current_user)):
    return await disable_email_otp_api(current_user["id"], payload.password)


@router.post("/email-otp/verify")
@limiter.limit("10/minute")
async def verify_email_otp(request: Request, payload: EmailOtpVerifyRequest):
    temp_token = request.headers.get("X-Email-OTP-Token")
    if not temp_token:
        return await core_response(
            status_code=400,
            message="Temporary token required"
        )
    return await verify_email_otp_api(temp_token, payload.code)


@router.get("/oauth/{provider}")
@limiter.limit("30/minute")
async def oauth_login(provider: str, request: Request):
    return await oauth_login_api(provider, request)


@router.get("/oauth/{provider}/callback")
@limiter.limit("30/minute")
async def oauth_callback(provider: str, request: Request):
    return await oauth_callback_api(provider, request)


@router.post("/set-session-cookie")
@limiter.limit("30/minute")
async def set_session_cookie_route(request: Request, payload: SetSessionCookieRequest):
    from utils.cookies import set_session_cookie
    response = Response(content='{"success": true}', media_type="application/json")
    return set_session_cookie(response, payload.session_id)
