from time import time
from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from features.auth.utils.two_factor import verify_totp_code
from utils.encryption import decrypt_data
from utils.session_manager import create_session
from bson import ObjectId
from logging_config import logger
from config import COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_DOMAIN, COOKIE_PARTITIONED
import hashlib


async def verify_2fa_login(temp_token: str, code: str):
    """Verify TOTP code during login using temporary token"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        # Hash the temp token and find user directly using indexed hash field (O(1) lookup)
        temp_token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
        user = await users_collection.find_one({
            "_2fa_temp_token_hash": temp_token_hash,
            "_2fa_temp_token_expires": {"$gt": int(time() * 1000)}
        })

        if not user:
            return await core_response(
                status_code=400,
                message="Invalid or expired temporary token"
            )

        # Decrypt the 2FA secret for verification
        try:
            decrypted_secret = decrypt_data(user["_2fa_secret"])
        except ValueError:
            return await core_response(
                status_code=500,
                message="Failed to decrypt 2FA secret"
            )

        # Verify TOTP code
        if not verify_totp_code(decrypted_secret, code):
            logger.warning(f"Invalid 2FA code for user ID: {user.get('_id')}")
            return await core_response(
                status_code=400,
                message="Invalid verification code"
            )

        # Clear temp token and hash
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$unset": {"_2fa_temp_token": 1, "_2fa_temp_token_hash": 1, "_2fa_temp_token_expires": 1}}
        )

        # Create session
        session_id = await create_session(str(user.get("_id")))

        logger.info(f"2FA verification successful for user ID: {user.get('_id')}")

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
        if COOKIE_PARTITIONED:
            cookie_kwargs["partitioned"] = True
        if COOKIE_DOMAIN:
            cookie_kwargs["domain"] = COOKIE_DOMAIN

        response.set_cookie(
            key="session_id",
            value=session_id,
            **cookie_kwargs
        )

        return response
    except Exception as e:
        logger.error(f"Error verifying 2FA: {e}")
        return await core_response(
            status_code=500,
            message="Failed to verify 2FA"
        )
