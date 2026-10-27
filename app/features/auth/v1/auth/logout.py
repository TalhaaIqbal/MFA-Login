from fastapi import Request
from utils.core_response import core_response
from utils.session_manager import revoke_session
from config import COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_DOMAIN


async def logout_api(request: Request):
    """
    Logout and revoke the current session.
    This invalidates the session preventing further use.
    """
    # Get the session ID from cookie
    session_id = request.cookies.get("session_id")

    # Revoke the session
    if session_id:
        await revoke_session(session_id)

    response = await core_response(
        status_code=200,
        message="Logged out successfully"
    )

    # Clear cookie with matching attributes
    cookie_delete_kwargs = {
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "path": "/"  # Important: set path to match when cookie was set
    }
    if COOKIE_DOMAIN:
        cookie_delete_kwargs["domain"] = COOKIE_DOMAIN

    response.delete_cookie(key="session_id", **cookie_delete_kwargs)

    return response
