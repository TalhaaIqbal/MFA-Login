from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from utils.email_otp import verify_otp
from bson import ObjectId
from logging_config import logger
from time import time


async def enable_email_otp(user_id: str, code: str, challenge_id: str = None):
    """Enable email OTP 2FA after verifying the code"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return await core_response(
                status_code=404,
                message="User not found"
            )

        # Guard check: if email OTP is already enabled
        if user.get("is_email_otp_enabled") is True:
            return await core_response(
                status_code=400,
                message="Email OTP is already enabled"
            )

        # Get the pending OTP from user document
        pending_otp = user.get("email_otp_pending")
        otp_expires = user.get("email_otp_pending_expires")

        if not pending_otp:
            logger.warning(f"No pending email OTP for user: {user_id}")
            return await core_response(
                status_code=400,
                message="No pending email OTP setup. Please setup email OTP again."
            )

        # Check if OTP has expired
        if otp_expires and int(time()) > otp_expires:
            logger.warning(f"Pending email OTP expired for user: {user_id}")
            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$unset": {"email_otp_pending": "", "email_otp_pending_expires": ""}}
            )
            return await core_response(
                status_code=400,
                message="Setup expired. Please setup email OTP again."
            )

        # Verify the code
        if not verify_otp(pending_otp, code):
            logger.warning(f"Invalid email OTP for user ID: {user_id}")
            return await core_response(
                status_code=400,
                message="Invalid verification code"
            )

        # Enable email OTP and clear pending OTP
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {"is_email_otp_enabled": True},
                "$unset": {"email_otp_pending": "", "email_otp_pending_expires": ""}
            }
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
