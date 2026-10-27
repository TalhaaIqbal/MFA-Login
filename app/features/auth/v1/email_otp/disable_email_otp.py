from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from bson import ObjectId
from logging_config import logger
from features.auth.utils.verify_password import verify_password


async def disable_email_otp(user_id: str, password: str = None):
    """Disable email OTP 2FA for the current user with password authentication"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return await core_response(
                status_code=404,
                message="User not found"
            )

        # Guard check: if email OTP is already disabled
        if user.get("is_email_otp_enabled") is not True:
            return await core_response(
                status_code=400,
                message="Email OTP is already disabled"
            )

        # Step-up authentication: require password
        if not password:
            return await core_response(
                status_code=400,
                message="Password required to disable email OTP"
            )

        # Verify password
        if not verify_password(password, user.get("password")):
            logger.warning(f"Invalid password for email OTP disable attempt by user {user_id}")
            return await core_response(
                status_code=401,
                message="Invalid password"
            )

        # Disable email OTP
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$unset": {"is_email_otp_enabled": 1}}
        )

        logger.info(f"Email OTP disabled successfully for user {user_id} with step-up authentication")

        return await core_response(
            status_code=200,
            message="Email OTP disabled successfully"
        )
    except Exception as e:
        logger.error(f"Error disabling email OTP: {e}")
        return await core_response(
            status_code=500,
            message="Failed to disable email OTP"
        )
