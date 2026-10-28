from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from bson import ObjectId
from logging_config import logger
from features.auth.utils.verify_password import verify_password
from utils.email_otp import verify_otp, generate_otp, send_email_otp


async def disable_email_otp(user_id: str, password: str = None, email_otp_code: str = None):
    """Disable email OTP 2FA for the current user with step-up authentication"""
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

        # Step-up authentication: require either password OR email OTP code
        if not password and not email_otp_code:
            return await core_response(
                status_code=400,
                message="Step-up authentication required: provide either password or email OTP code"
            )

        # Verify password if provided
        if password:
            if not verify_password(password, user.get("password")):
                logger.warning(f"Invalid password for email OTP disable attempt by user {user_id}")
                return await core_response(
                    status_code=401,
                    message="Invalid password"
                )

        # Verify email OTP code if provided
        if email_otp_code:
            if not user.get("email_otp"):
                logger.warning(f"No email OTP stored for user {user_id}. Request a new code first.")
                return await core_response(
                    status_code=400,
                    message="No email OTP code available. Please request a new code first."
                )
            if not verify_otp(user.get("email_otp"), email_otp_code):
                logger.warning(f"Invalid email OTP code for disable attempt by user {user_id}")
                return await core_response(
                    status_code=401,
                    message="Invalid email OTP code"
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


async def send_disable_email_otp(user_id: str, email: str):
    """Send email OTP for disabling email OTP"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return await core_response(
                status_code=404,
                message="User not found"
            )

        # Check if email OTP is enabled
        if user.get("is_email_otp_enabled") is not True:
            return await core_response(
                status_code=400,
                message="Email OTP is not enabled"
            )

        # Generate and send OTP
        otp = generate_otp()
        await send_email_otp(email, otp)

        # Store OTP in user document
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"email_otp": otp}}
        )

        logger.info(f"Email OTP sent for disable to user {user_id}")

        return await core_response(
            status_code=200,
            message="Email OTP sent successfully"
        )
    except Exception as e:
        logger.error(f"Error sending email OTP for disable: {e}")
        return await core_response(
            status_code=500,
            message="Failed to send email OTP"
        )
