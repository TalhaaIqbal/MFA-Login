from time import time
from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from utils.email_otp import verify_otp
from utils.session_manager import create_session
from bson import ObjectId
from logging_config import logger
from utils.cookies import set_session_cookie
import hashlib


async def verify_email_otp_login(temp_token: str, code: str):
    """Verify email OTP code during login using temporary token"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        # Hash the temp token and find user directly using indexed hash field (O(1) lookup)
        temp_token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
        user = await users_collection.find_one({
            "_email_otp_temp_token_hash": temp_token_hash,
            "_email_otp_temp_token_expires": {"$gt": int(time() * 1000)}
        })

        if not user:
            return await core_response(
                status_code=400,
                message="Invalid or expired temporary token"
            )

        # Verify email OTP code
        if not verify_otp(user["_email_otp_temp"], code):
            logger.warning(f"Invalid email OTP for user ID: {user.get('_id')}")
            return await core_response(
                status_code=400,
                message="Invalid verification code"
            )

        # Clear temp token and OTP
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$unset": {"_email_otp_temp": 1, "_email_otp_temp_token": 1, "_email_otp_temp_token_hash": 1, "_email_otp_temp_token_expires": 1}}
        )

        # Create session
        session_id = await create_session(str(user.get("_id")))

        logger.info(f"Email OTP verification successful for user ID: {user.get('_id')}")

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
