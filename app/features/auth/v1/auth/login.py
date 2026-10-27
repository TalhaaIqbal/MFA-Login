from time import time
from logging_config import logger, redact_email
from models.auth.auth import LoginRequest
from utils.core_response import core_response
from db.db import get_db_conn
from db.collection import DBCollection
from features.auth.utils.verify_password import verify_password
from utils.encryption import encrypt_data
from utils.session_manager import create_session
from utils.cookies import set_session_cookie
import secrets
import hashlib


async def login(payload: LoginRequest):
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        logger.info(f"Login attempt for email: {redact_email(payload.email)}")

        user = await users_collection.find_one({"email": payload.email})
        if not user:
            logger.warning(f"User not found: {redact_email(payload.email)}")
            return await core_response(
                status_code=401,
                message="Invalid email or password"
            )

        if not user.get("password") or not verify_password(payload.password, user["password"]):
            logger.warning(f"Invalid password for email: {redact_email(payload.email)}")
            return await core_response(
                status_code=401,
                message="Invalid email or password"
            )

        # Check if 2FA is enabled (TOTP or Email OTP)
        is_2fa_enabled = user.get("is_2fa_enabled", False)
        is_email_otp_enabled = user.get("is_email_otp_enabled", False)

        if is_2fa_enabled:
            # Generate temporary token for TOTP 2FA verification
            temp_token = secrets.token_urlsafe(32)
            temp_token_expires = int(time() * 1000) + (5 * 60 * 1000)  # 5 minutes

            # Hash temp token for efficient lookup (hash instead of encrypt for O(1) query)
            temp_token_hash = hashlib.sha256(temp_token.encode()).hexdigest()

            # Store hash and encrypted temp token in user document
            await users_collection.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "_2fa_temp_token_hash": temp_token_hash,
                        "_2fa_temp_token": encrypt_data(temp_token),
                        "_2fa_temp_token_expires": temp_token_expires
                    }
                }
            )

            logger.info(f"TOTP 2FA required for user ID: {user.get('_id')}")

            return await core_response(
                status_code=200,
                message="2FA verification required",
                data={
                    "requires_2fa": True,
                    "mfa_method": "totp",
                    "temp_token": temp_token,
                    "user_id": str(user.get("_id"))
                }
            )

        if is_email_otp_enabled:
            # Generate temporary token for email OTP verification
            temp_token = secrets.token_urlsafe(32)
            temp_token_expires = int(time() * 1000) + (10 * 60 * 1000)  # 10 minutes

            # Hash temp token for efficient lookup
            temp_token_hash = hashlib.sha256(temp_token.encode()).hexdigest()

            # Generate and send email OTP
            from utils.email_otp import generate_otp, send_email_otp
            otp = generate_otp()
            await send_email_otp(user.get("email"), otp)

            # Store hash, temp token, and OTP in user document
            await users_collection.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "_email_otp_temp_token_hash": temp_token_hash,
                        "_email_otp_temp_token": encrypt_data(temp_token),
                        "_email_otp_temp_token_expires": temp_token_expires,
                        "_email_otp_temp": otp
                    }
                }
            )

            logger.info(f"Email OTP required for user ID: {user.get('_id')}")

            return await core_response(
                status_code=200,
                message="Email OTP verification required",
                data={
                    "requires_2fa": True,
                    "mfa_method": "email",
                    "temp_token": temp_token,
                    "user_id": str(user.get("_id"))
                }
            )

        # No 2FA - proceed with normal login
        session_id = await create_session(str(user.get("_id")))

        logger.info(f"Login successful for user ID: {user.get('_id')}")

        response = await core_response(
            status_code=200,
            message="Login successful",
            data={
                "user_details": {
                    "id": str(user.get("_id")),
                    "email": user.get("email"),
                    "full_name": user.get("full_name"),
                    "role": user.get("role"),
                    "is_2fa_enabled": user.get("is_2fa_enabled", False),
                },
            }
        )

        set_session_cookie(response, session_id)

        return response

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return await core_response(
            status_code=500,
            message="Internal server error"
        )