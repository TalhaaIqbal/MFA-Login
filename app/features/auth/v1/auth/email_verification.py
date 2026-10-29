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
        pending_collection = DBCollection.PENDING_EMAIL_VERIFICATIONS(db_conn)

        # Normalize email to lowercase
        email = email.lower()

        # Check if user already exists in users collection
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

        # Store pending verification data in separate collection
        from features.auth.utils.hash_password import hash_password
        from time import time

        hashed_password = hash_password(password)
        now = int(time() * 1000)

        pending_verification = {
            "email": email,
            "password": hashed_password,
            "full_name": name,
            "role": "user",
            "verification_token": verification_token,
            "verification_token_expires_at": int((now + (24 * 60 * 60 * 1000))),  # 24 hours
            "created_at": now
        }

        # Check if there's already a pending verification for this email
        existing_pending = await pending_collection.find_one({"email": email})
        if existing_pending:
            # Update existing pending verification
            await pending_collection.update_one(
                {"_id": existing_pending["_id"]},
                {"$set": pending_verification}
            )
            logger.info(f"Updated pending email verification for {email}")
        else:
            # Insert new pending verification
            await pending_collection.insert_one(pending_verification)
            logger.info(f"Created pending email verification for {email}")

        # Send verification email
        await send_email_verification(email, verification_link)

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
    """Verify email and complete signup by creating user account"""
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
        pending_collection = DBCollection.PENDING_EMAIL_VERIFICATIONS(db_conn)

        # Find pending verification
        pending_verification = await pending_collection.find_one({"email": email})

        if not pending_verification:
            return await core_response(
                status_code=400,
                message="No pending signup found or already verified"
            )

        # Check if token has expired in database
        from time import time
        current_time = int(time() * 1000)
        if pending_verification.get("verification_token_expires_at", 0) < current_time:
            # Delete expired pending verification
            await pending_collection.delete_one({"email": email})
            return await core_response(
                status_code=400,
                message="Verification link has expired. Please sign up again."
            )

        # Create actual user account
        from time import time
        now = int(time() * 1000)

        new_user = {
            "email": pending_verification["email"],
            "password": pending_verification["password"],
            "full_name": pending_verification["full_name"],
            "role": pending_verification["role"],
            "is_2fa_enabled": False,
            "is_email_verified": True,
            "created_at": now,
            "updated_at": now
        }

        result = await user_collection.insert_one(new_user)
        logger.info(f"Created user account for {email} after email verification")

        # Delete pending verification
        await pending_collection.delete_one({"email": email})
        logger.info(f"Deleted pending verification for {email}")

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


async def cleanup_expired_pending_verifications():
    """Clean up expired pending email verifications"""
    try:
        db_conn = await get_db_conn()
        pending_collection = DBCollection.PENDING_EMAIL_VERIFICATIONS(db_conn)

        from time import time
        current_time = int(time() * 1000)

        result = await pending_collection.delete_many({
            "verification_token_expires_at": {"$lt": current_time}
        })

        logger.info(f"Cleaned up {result.deleted_count} expired pending email verifications")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up expired pending verifications: {e}")
        return 0
