from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from bson import ObjectId
from logging_config import logger
from utils.jwt_tokens import create_email_verification_token, verify_email_verification_token
from utils.email_otp import send_email_verification
from config import FRONTEND_URL


async def initiate_email_verification(email: str, name: str, password: str):
    """Initiate signup by sending email verification"""
    try:
        db_conn = await get_db_conn()
        user_collection = DBCollection.USERS(db_conn)

        # Normalize email to lowercase
        email = email.lower()

        # Check if user already exists
        existing_user = await user_collection.find_one({"email": email})
        if existing_user:
            logger.warning(f"User already exists: {email}")
            return await core_response(
                status_code=400,
                message="Email already registered"
            )

        # Generate email verification token
        verification_token = create_email_verification_token(email, expires_in_hours=24)

        # Create verification link
        verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"

        # Store pending signup data temporarily (you could also use Redis)
        # For now, we'll store it in the user collection with a special flag
        from features.auth.utils.hash_password import hash_password
        from time import time

        hashed_password = hash_password(password)
        now = int(time() * 1000)

        # Store as pending user
        pending_user = {
            "email": email,
            "password": hashed_password,
            "full_name": name,
            "role": "user",
            "is_2fa_enabled": False,
            "is_email_verified": False,
            "verification_token": verification_token,
            "verification_token_expires_at": int((now + (24 * 60 * 60 * 1000))),  # 24 hours
            "created_at": now,
            "updated_at": now
        }

        # Check if there's already a pending signup for this email
        existing_pending = await user_collection.find_one({"email": email, "is_email_verified": False})
        if existing_pending:
            # Update existing pending user
            await user_collection.update_one(
                {"_id": existing_pending["_id"]},
                {"$set": pending_user}
            )
        else:
            # Insert new pending user
            await user_collection.insert_one(pending_user)

        # Send verification email
        await send_email_verification(email, verification_link)

        logger.info(f"Email verification initiated for {email}")

        return await core_response(
            status_code=200,
            message="Verification email sent. Please check your inbox to complete signup.",
            data={"email": email}
        )

    except Exception as e:
        logger.error(f"Error initiating email verification: {e}")
        return await core_response(
            status_code=500,
            message="Failed to send verification email"
        )


async def verify_email(token: str):
    """Verify email and complete signup"""
    try:
        # Verify token
        token_data = verify_email_verification_token(token)
        if not token_data:
            return await core_response(
                status_code=400,
                message="Invalid or expired verification link"
            )

        email = token_data["email"].lower()

        db_conn = await get_db_conn()
        user_collection = DBCollection.USERS(db_conn)

        # Find pending user
        pending_user = await user_collection.find_one({
            "email": email,
            "is_email_verified": False
        })

        if not pending_user:
            return await core_response(
                status_code=400,
                message="No pending signup found or already verified"
            )

        # Mark email as verified
        await user_collection.update_one(
            {"_id": pending_user["_id"]},
            {
                "$set": {"is_email_verified": True},
                "$unset": {"verification_token": 1, "verification_token_expires_at": 1}
            }
        )

        logger.info(f"Email verified successfully for {email}")

        return await core_response(
            status_code=200,
            message="Email verified successfully. You can now login.",
            data={"email": email}
        )

    except Exception as e:
        logger.error(f"Error verifying email: {e}")
        return await core_response(
            status_code=500,
            message="Failed to verify email"
        )
