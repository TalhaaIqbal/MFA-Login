from config import COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_DOMAIN

COOKIE_NAME = "session_id"


def _opts() -> dict:
    opts = {"path": "/", "secure": COOKIE_SECURE, "samesite": COOKIE_SAMESITE, "httponly": True}
    if COOKIE_DOMAIN:
        opts["domain"] = COOKIE_DOMAIN
    return opts


def set_session_cookie(response, session_id: str):
    response.set_cookie(COOKIE_NAME, session_id, **_opts())
    return response


def clear_session_cookie(response):
    response.delete_cookie(COOKIE_NAME, **_opts())
    return response
