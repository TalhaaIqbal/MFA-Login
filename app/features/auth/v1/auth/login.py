from time import time
from logging_config import logger, redact_email
from models.auth.auth import LoginRequest
from utils.core_response import core_response
from db.db import get_db_conn
from db.collection import DBCollection
from features.auth.utils.verify_password import verify_password
from utils.encryption import encrypt_data
from utils.session_manager import create_session
from config import COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_DOMAIN
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

        if not verify_password(payload.password, user.get("password")):
            logger.warning(f"Invalid password for email: {redact_email(payload.email)}")
            return await core_response(
                status_code=401,
                message="Invalid email or password"
            )

        # Check if 2FA is enabled
        is_2fa_enabled = user.get("is_2fa_enabled", False)

        if is_2fa_enabled:
            # Generate temporary token for 2FA verification
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

            logger.info(f"2FA required for user ID: {user.get('_id')}")

            return await core_response(
                status_code=200,
                message="2FA verification required",
                data={
                    "requires_2fa": True,
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

        # Set HttpOnly cookie for session
        cookie_kwargs = {
            "httponly": True,
            "secure": COOKIE_SECURE,
            "samesite": COOKIE_SAMESITE,
            "path": "/",  # Important: set path explicitly
            "max_age": 604800  # 7 days
        }
        if COOKIE_DOMAIN:
            cookie_kwargs["domain"] = COOKIE_DOMAIN

        response.set_cookie(
            key="session_id",
            value=session_id,
            **cookie_kwargs
        )

        return response

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return await core_response(
            status_code=500,
            message="Internal server error"
        )