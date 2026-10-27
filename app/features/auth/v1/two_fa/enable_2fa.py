from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from features.auth.utils.two_factor import verify_totp_code
from utils.encryption import decrypt_data
from bson import ObjectId
from logging_config import logger


async def enable_2fa(user_id: str, code: str, challenge_id: str = None):
    """Enable 2FA after verifying the code"""
    try:
        logger.info(f"enable_2fa called with user_id: {user_id}, code: {code}")

        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user or "_2fa_secret" not in user:
            logger.warning(f"2FA not setup for user: {user_id}")
            return await core_response(
                status_code=400,
                message="2FA not setup. Please setup 2FA first."
            )

        # Guard check: if 2FA is already enabled
        if user.get("is_2fa_enabled") is True:
            logger.warning(f"2FA already enabled for user: {user_id}")
            return await core_response(
                status_code=400,
                message="2FA is already enabled"
            )

        # Decrypt the secret before verification
        try:
            decrypted_secret = decrypt_data(user["_2fa_secret"])
            logger.info(f"Decrypted secret length: {len(decrypted_secret)} for user ID: {user_id}")
        except ValueError as e:
            logger.error(f"Failed to decrypt 2FA secret for user ID: {user_id}: {e}")
            return await core_response(
                status_code=500,
                message="Failed to decrypt 2FA secret"
            )

        # Verify the code
        logger.info(f"Verifying TOTP code for user ID: {user_id}, code: {code}")
        if not verify_totp_code(decrypted_secret, code):
            logger.warning(f"Invalid 2FA code for user ID: {user_id}")
            return await core_response(
                status_code=400,
                message="Invalid verification code"
            )

        # Enable 2FA
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_2fa_enabled": True}}
        )

        if result.modified_count == 0:
            logger.warning(f"No document modified for user ID: {user_id}")
            return await core_response(
                status_code=500,
                message="Failed to update user document"
            )

        logger.info(f"2FA enabled successfully for user ID: {user_id}")
        return await core_response(
            status_code=200,
            message="2FA enabled successfully"
        )
    except Exception as e:
        logger.error(f"Error enabling 2FA: {e}", exc_info=True)
        return await core_response(
            status_code=500,
            message="Failed to enable 2FA"
        )
