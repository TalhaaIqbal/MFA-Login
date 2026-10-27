from fastapi import Response
from config import FRONTEND_URL, ENVIRONMENT


def set_oauth_cookie(session_id: str):
    # In production with cross-domain setup, pass session_id as query param
    # Browser blocks cross-domain cookies on redirects
    if ENVIRONMENT == "production":
        response = Response(status_code=302, headers={"Location": f"{FRONTEND_URL}/oauth/callback?session_id={session_id}"})
    else:
        # Local development: use cookie
        from utils.cookies import set_session_cookie
        response = Response(status_code=302, headers={"Location": f"{FRONTEND_URL}/oauth/callback"})
        response = set_session_cookie(response, session_id)
    return response
