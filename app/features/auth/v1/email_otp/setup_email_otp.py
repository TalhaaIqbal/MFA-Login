from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from utils.email_otp import generate_otp, send_email_otp
from utils.auth_challenges import create_challenge
from bson import ObjectId
from logging_config import logger


async def setup_email_otp(user_id: str, email: str):
    """Setup email OTP 2FA for the current user"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        # Check if user exists
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return await core_response(
                status_code=404,
                message="User not found"
            )

        # Check if email OTP is already enabled
        if user.get("is_email_otp_enabled") is True:
            return await core_response(
                status_code=400,
                message="Email OTP is already enabled. Disable it first to set up again."
            )

        # Generate OTP
        otp = generate_otp()

        # Send OTP to email
        await send_email_otp(email, otp)

        # Store OTP in auth_challenges (not enabled yet)
        challenge_id = await create_challenge(
            user_id=user_id,
            challenge_type="email_otp_setup",
            challenge_data=otp,
            expires_in_minutes=10
        )

        logger.info(f"Email OTP setup initiated for user {user_id}")

        return await core_response(
            status_code=200,
            message="Email OTP setup initiated. Check your email for the verification code.",
            data={
                "message": "OTP sent to your email",
                "challenge_id": challenge_id
            }
        )
    except Exception as e:
        logger.error(f"Error setting up email OTP: {e}")
        return await core_response(
            status_code=500,
            message="Failed to setup email OTP"
        )
