from fastapi import Response
from config import COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_DOMAIN, COOKIE_PARTITIONED, FRONTEND_URL


def set_oauth_cookie(session_id: str):
    """Create response with OAuth cookie and redirect"""
    response = Response(status_code=302)
    response.headers["Location"] = f"{FRONTEND_URL}/dashboard"

    cookie_kwargs = {
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "path": "/",
        "max_age": 604800
    }
    if COOKIE_PARTITIONED:
        cookie_kwargs["partitioned"] = True
    if COOKIE_DOMAIN:
        cookie_kwargs["domain"] = COOKIE_DOMAIN

    response.set_cookie(key="session_id", value=session_id, **cookie_kwargs)

    return response
