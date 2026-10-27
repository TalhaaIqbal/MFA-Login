from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from utils.email_otp import verify_otp
from bson import ObjectId
from logging_config import logger


async def enable_email_otp(user_id: str, code: str, challenge_id: str = None):
    """Enable email OTP 2FA after verifying the code"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user or "email_otp" not in user:
            logger.warning(f"Email OTP not setup for user: {user_id}")
            return await core_response(
                status_code=400,
                message="Email OTP not setup. Please setup email OTP first."
            )

        # Guard check: if email OTP is already enabled
        if user.get("is_email_otp_enabled") is True:
            return await core_response(
                status_code=400,
                message="Email OTP is already enabled"
            )

        # Verify the code
        if not verify_otp(user["email_otp"], code):
            logger.warning(f"Invalid email OTP for user ID: {user_id}")
            return await core_response(
                status_code=400,
                message="Invalid verification code"
            )

        # Enable email OTP
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_email_otp_enabled": True}}
        )

        logger.info(f"Email OTP enabled successfully for user {user_id}")

        return await core_response(
            status_code=200,
            message="Email OTP enabled successfully"
        )
    except Exception as e:
        logger.error(f"Error enabling email OTP: {e}")
        return await core_response(
            status_code=500,
            message="Failed to enable email OTP"
        )
