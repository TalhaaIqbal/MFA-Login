# Path: features/users/v1/update_user.py
from db.db import get_db_conn
from db.collection import DBCollection
from logging_config import logger
from utils.core_response import core_response
from bson import ObjectId
from utils.session_manager import revoke_all_user_sessions


async def update_user(user_id: str, update_data: dict):
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        object_id = ObjectId(user_id)
        user = await users_collection.find_one({"_id": object_id})

        if not user:
            return await core_response(
                status_code=404,
                message="user not found"
            )

        # Check if password is being changed
        password_changed = "password" in update_data

        # Update user with provided data
        update_result = await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )

        logger.info(f"Update result modified_count: {update_result.modified_count}")

        if update_result.modified_count == 0:
            return await core_response(
                status_code=200,
                message="no changes made to user"
            )

        # Revoke all sessions if password was changed
        if password_changed:
            revoked_count = await revoke_all_user_sessions(user_id)
            logger.info(f"Revoked {revoked_count} sessions for user {user_id} due to password change")

        # Get updated user
        updated_user = await users_collection.find_one(
            {"_id": user["_id"]},
            {
                "password": 0,
                "_2fa_secret": 0,
                "_2fa_temp_token": 0,
                "_2fa_temp_token_expires": 0
            }
        )

        logger.info(f"User {user_id} updated successfully")

        return await core_response(
            status_code=200,
            message="user updated successfully",
            data=updated_user
        )
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise
