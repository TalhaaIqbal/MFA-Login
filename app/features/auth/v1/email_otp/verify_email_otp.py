from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from utils.email_otp import verify_otp
from utils.session_manager import create_session
from utils.jwt_tokens import verify_temp_token
from bson import ObjectId
from logging_config import logger
from utils.cookies import set_session_cookie


async def verify_email_otp_login(temp_token: str, code: str):
    """Verify email OTP code during login using temporary JWT token"""
    try:
        # Verify JWT token and get user_id
        token_data = verify_temp_token(temp_token, "email_otp_login")

        if not token_data:
            return await core_response(
                status_code=400,
                message="Invalid or expired temporary token"
            )

        user_id = token_data["user_id"]

        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        # Get user data
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return await core_response(
                status_code=404,
                message="User not found"
            )

        # Get stored OTP
        stored_otp = user.get("email_otp")

        if not stored_otp:
            logger.warning(f"No email OTP found for user ID: {user_id}")
            return await core_response(
                status_code=400,
                message="No OTP found. Please request a new one."
            )

        # Verify email OTP code
        if not verify_otp(stored_otp, code):
            logger.warning(f"Invalid email OTP for user ID: {user_id}")
            return await core_response(
                status_code=400,
                message="Invalid verification code"
            )

        # Clear OTP from user document
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$unset": {"email_otp": ""}}
        )

        # Create session
        session_id = await create_session(user_id)

        logger.info(f"Email OTP verification successful for user ID: {user_id}")

        response = await core_response(
            status_code=200,
            message="Login successful",
            data={
                "user_details": {
                    "id": str(user.get("_id")),
                    "email": user.get("email"),
                    "full_name": user.get("full_name"),
                    "role": user.get("role"),
                    "is_email_otp_enabled": user.get("is_email_otp_enabled", False),
                },
            }
        )

        set_session_cookie(response, session_id)

        return response
    except Exception as e:
        logger.error(f"Error verifying email OTP: {e}")
        return await core_response(
            status_code=500,
            message="Failed to verify email OTP"
        )
