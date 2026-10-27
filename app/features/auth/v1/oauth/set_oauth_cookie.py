from fastapi import Response
from config import FRONTEND_URL
from utils.cookies import set_session_cookie


def set_oauth_cookie(session_id: str):
    response = Response(status_code=302, headers={"Location": f"{FRONTEND_URL}/oauth/callback"})
    return set_session_cookie(response, session_id)
