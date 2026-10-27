from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from utils.email_otp import verify_otp
from utils.auth_challenges import get_challenge_data, verify_and_consume_challenge
from bson import ObjectId
from logging_config import logger


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

        # Get the OTP from challenge
        if not challenge_id:
            return await core_response(
                status_code=400,
                message="Challenge ID required"
            )

        challenge_data = await get_challenge_data(challenge_id, "email_otp_setup")
        if not challenge_data:
            return await core_response(
                status_code=400,
                message="Invalid or expired challenge. Please setup email OTP again."
            )

        # Verify user matches
        if challenge_data["user_id"] != user_id:
            return await core_response(
                status_code=400,
                message="Invalid challenge"
            )

        # Verify the code
        if not verify_otp(challenge_data["challenge_data"], code):
            return await core_response(
                status_code=400,
                message="Invalid verification code"
            )

        # Consume the challenge
        await verify_and_consume_challenge(challenge_id, "email_otp_setup", challenge_data["challenge_data"])

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
