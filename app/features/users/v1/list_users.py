# Path: features/users/v1/list_users.py
from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from logging_config import logger


async def list_users():
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        # Exclude sensitive fields: password and all 2FA-related fields
        users = await users_collection.find(
            {},
            {
                "password": 0,
                "_2fa_secret": 0,
                "_2fa_temp_token": 0,
                "_2fa_temp_token_expires": 0
            }
        ).to_list(length=None)

        logger.info(f"Users retrieved successfully: {len(users)} users")

        return await core_response(
            status_code=200,
            message="users retrieved successfully",
            data=users
        )
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise
