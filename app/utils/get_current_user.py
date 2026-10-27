from typing import Annotated

from fastapi import Depends, HTTPException, status, Request
from logging_config import logger
from utils.session_manager import verify_session


def _unauthorized(detail: str = "Could not validate credentials.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


async def get_current_user(
    request: Request,
) -> dict:
    # Get session ID from cookie
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise _unauthorized("Session not found")

    # Verify session and get user data
    user_data = await verify_session(session_id)

    if not user_data:
        raise _unauthorized("Invalid or expired session")

    return user_data


def _forbidden(detail: str = "Access forbidden.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Dependency that ensures the current user is an admin."""
    if current_user.get("role") != "admin":
        logger.warning("access_denied user_id=%s role=%s action=admin_required", current_user.get("id"), current_user.get("role"))
        raise _forbidden("Only admin users can access this resource.")
    return current_user