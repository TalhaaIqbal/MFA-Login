from fastapi import Request
from utils.core_response import core_response
from utils.session_manager import revoke_session
from utils.cookies import clear_session_cookie, COOKIE_NAME


async def logout_api(request: Request):
    session_id = request.cookies.get(COOKIE_NAME)
    if session_id:
        await revoke_session(session_id)

    response = await core_response(status_code=200, message="Logged out successfully")
    return clear_session_cookie(response)
