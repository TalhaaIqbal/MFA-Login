from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from features.auth.utils.two_factor import generate_totp_secret, generate_qr_code
from utils.encryption import encrypt_data
from bson import ObjectId
from logging_config import logger
from time import time


async def setup_2fa(user_id: str, email: str):
    """Setup 2FA for the current user"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        # Check if 2FA is already enabled
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return await core_response(
                status_code=404,
                message="User not found"
            )

        # Security: Prevent overwriting secret if 2FA is already enabled
        if user.get("is_2fa_enabled") is True:
            return await core_response(
                status_code=400,
                message="2FA is already enabled. Disable it first to set up a new authenticator."
            )

        # Generate new secret
        secret = generate_totp_secret()
        qr_code = generate_qr_code(secret, email)

        # Encrypt secret before storing
        encrypted_secret = encrypt_data(secret)

        # Store encrypted secret in user document (not enabled yet)
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "_2fa_secret_pending": encrypted_secret,
                    "_2fa_secret_pending_expires": int(time()) + 600  # 10 minutes
                }
            }
        )

        logger.info(f"2FA setup initiated for user {user_id}")

        return await core_response(
            status_code=200,
            message="2FA setup initiated",
            data={
                "secret": secret,
                "qr_code": qr_code
            }
        )
    except Exception as e:
        logger.error(f"Error setting up 2FA: {e}")
        return await core_response(
            status_code=500,
            message="Failed to setup 2FA"
        )
