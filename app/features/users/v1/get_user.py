# Path: features/users/v1/get_user.py
from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from bson import ObjectId
from logging_config import logger


async def get_user(user_id: str):
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        projection = {
            "password": 0,  # no password
            "_2fa_secret": 0,  # no 2FA secret
            "_2fa_temp_token": 0,  # no temp token
            "_2fa_temp_token_expires": 0  # no temp token expiry
        }


        object_id = ObjectId(user_id)
        user = await users_collection.find_one(
            {"_id": object_id},
            projection
        )

        if not user:
            return await core_response(
                status_code=404,
                message="user not found"
            )


        return await core_response(
            status_code=200,
            message="user retrieved successfully",
            data=user
        )
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise
