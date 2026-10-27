# Path: features/users/v1/delete_user.py
from db.db import get_db_conn
from db.collection import DBCollection
from logging_config import logger
from utils.core_response import core_response
from bson import ObjectId
from utils.session_manager import revoke_all_user_sessions


async def delete_user(user_id: str, current_user_id: str = None):
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        logger.info(f"Deleting user {user_id}")

        object_id = ObjectId(user_id)
        user = await users_collection.find_one({"_id": object_id})

        if not user:
            return await core_response(
                status_code=404,
                message="User not found"
            )

        # Prevent self-deletion
        if current_user_id and user_id == current_user_id:
            return await core_response(
                status_code=403,
                message="Cannot delete your own account"
            )

        # Prevent deletion of the last admin
        if user.get("role") == "admin":
            admin_count = await users_collection.count_documents({"role": "admin"})
            if admin_count <= 1:
                return await core_response(
                    status_code=403,
                    message="Cannot delete the last admin user"
                )

        # Revoke all sessions before deleting user
        revoked_count = await revoke_all_user_sessions(user_id)
        logger.info(f"Revoked {revoked_count} sessions for user {user_id} before deletion")

        await users_collection.delete_one({"_id": object_id})

        logger.info(f"User {user_id} deleted successfully")

        return await core_response(
            status_code=200,
            message="User deleted successfully"
        )
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise
