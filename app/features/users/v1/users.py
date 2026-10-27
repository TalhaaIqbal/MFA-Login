# Path: features/users/v1/users.py
from .list_users import list_users
from .get_user import get_user
from .update_user import update_user
from .delete_user import delete_user


async def list_users_api():
    return await list_users()


async def get_user_api(user_id: str):
    return await get_user(user_id)


async def update_user_api(user_id: str, update_data: dict):
    return await update_user(user_id, update_data)


async def delete_user_api(user_id: str, current_user_id: str = None):
    return await delete_user(user_id, current_user_id)