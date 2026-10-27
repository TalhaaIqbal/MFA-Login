from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from features.auth.utils.two_factor import verify_totp_code
from utils.encryption import decrypt_data
from utils.session_manager import create_session
from utils.jwt_tokens import verify_temp_token
from bson import ObjectId
from logging_config import logger
from utils.cookies import set_session_cookie


async def verify_2fa_login(temp_token: str, code: str):
    """Verify TOTP code during login using temporary JWT token"""
    try:
        # Verify JWT token and get user_id
        token_data = verify_temp_token(temp_token, "totp_login")

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

        # Decrypt the 2FA secret for verification
        try:
            decrypted_secret = decrypt_data(user["_2fa_secret"])
            logger.info(f"Decrypted secret length: {len(decrypted_secret)} for user ID: {user_id}")
        except ValueError as e:
            logger.error(f"Failed to decrypt 2FA secret for user ID: {user_id}: {e}")
            return await core_response(
                status_code=500,
                message="Failed to decrypt 2FA secret"
            )

        # Verify TOTP code
        logger.info(f"Verifying TOTP code for user ID: {user_id}, code: {code}")
        if not verify_totp_code(decrypted_secret, code):
            logger.warning(f"Invalid 2FA code for user ID: {user_id}")
            return await core_response(
                status_code=400,
                message="Invalid verification code"
            )

        # Create session
        session_id = await create_session(user_id)

        logger.info(f"2FA verification successful for user ID: {user_id}")

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
        logger.error(f"Error verifying 2FA: {e}")
        return await core_response(
            status_code=500,
            message="Failed to verify 2FA"
        )
