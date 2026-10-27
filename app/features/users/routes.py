from fastapi import APIRouter, Request, Depends
from .v1.users import list_users_api, update_user_api, get_user_api, delete_user_api
from utils.core_response import core_response
from logging_config import logger
from models.auth.user import UserUpdate
from middlewares.limiter import limiter
from utils.get_current_user import get_current_user


router = APIRouter()



@router.get("")
@limiter.limit("100/minute")
async def list_users(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Only admin can list all users
        if current_user.get("role") != "admin":
            return await core_response(
                status_code=403,
                message="Only admin can list users"
            )
        return await list_users_api()
    except Exception as e:
        logger.error(f"Error in list_users route: {e}")
        return await core_response(
            status_code=500,
            message="Internal server error"
        )


@router.get("/{user_id}")
@limiter.limit("100/minute")
async def get_user(
    request: Request,
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Users can only view their own profile, admins can view any
        if current_user.get("role") != "admin" and current_user.get("id") != user_id:
            return await core_response(
                status_code=403,
                message="You can only view your own profile"
            )
        return await get_user_api(user_id)
    except Exception as e:
        logger.error(f"Error in get_user route: {e}")
        return await core_response(
            status_code=500,
            message="Internal server error"
        )


@router.put("/{user_id}")
@limiter.limit("60/minute")
async def update_user(
    request: Request,
    user_id: str,
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Users can only update their own profile, admins can update any
        if current_user.get("role") != "admin" and current_user.get("id") != user_id:
            return await core_response(
                status_code=403,
                message="You can only update your own profile"
            )
        return await update_user_api(user_id, update_data.model_dump(exclude_none=True))
    except Exception as e:
        logger.error(f"Error in update_user route: {e}")
        return await core_response(
            status_code=500,
            message="Internal server error"
        )


@router.delete("/{user_id}")
@limiter.limit("30/minute")
async def delete_user(
    request: Request,
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Only admin can delete users
        if current_user.get("role") != "admin":
            return await core_response(
                status_code=403,
                message="Only admin can delete users"
            )
        return await delete_user_api(user_id, current_user.get("id"))
    except Exception as e:
        logger.error(f"Error in delete_user route: {e}")
        return await core_response(
            status_code=500,
            message="Internal server error"
        )
