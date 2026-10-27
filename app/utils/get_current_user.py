from typing import Annotated
import asyncio

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

    # Verify session and get user data with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            user_data = await verify_session(session_id)
            if not user_data:
                raise _unauthorized("Invalid or expired session")
            return user_data
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to verify session after {max_retries} attempts: {e}")
                raise _unauthorized("Session verification failed")
            logger.warning(f"Session verification attempt {attempt + 1} failed, retrying...")
            await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff


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