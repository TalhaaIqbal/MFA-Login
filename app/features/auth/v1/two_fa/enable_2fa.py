from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from features.auth.utils.two_factor import verify_totp_code
from utils.encryption import decrypt_data
from utils.auth_challenges import get_challenge_data, verify_and_consume_challenge
from bson import ObjectId
from logging_config import logger


async def enable_2fa(user_id: str, code: str, challenge_id: str = None):
    """Enable 2FA after verifying the code"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return await core_response(
                status_code=404,
                message="User not found"
            )

        # Guard check: if 2FA is already enabled
        if user.get("is_2fa_enabled") is True:
            return await core_response(
                status_code=400,
                message="2FA is already enabled"
            )

        # Get the encrypted secret from challenge
        if not challenge_id:
            return await core_response(
                status_code=400,
                message="Challenge ID required"
            )

        challenge_data = await get_challenge_data(challenge_id, "totp_setup")
        if not challenge_data:
            return await core_response(
                status_code=400,
                message="Invalid or expired challenge. Please setup 2FA again."
            )

        # Verify user matches
        if challenge_data["user_id"] != user_id:
            return await core_response(
                status_code=400,
                message="Invalid challenge"
            )

        # Decrypt the secret before verification
        try:
            decrypted_secret = decrypt_data(challenge_data["challenge_data"])
        except ValueError:
            return await core_response(
                status_code=500,
                message="Failed to decrypt 2FA secret"
            )

        # Verify the code
        if not verify_totp_code(decrypted_secret, code):
            return await core_response(
                status_code=400,
                message="Invalid verification code"
            )

        # Consume the challenge
        await verify_and_consume_challenge(challenge_id, "totp_setup", challenge_data["challenge_data"])

        # Store the secret in user document and enable 2FA
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_2fa_enabled": True, "_2fa_secret": challenge_data["challenge_data"]}}
        )

        return await core_response(
            status_code=200,
            message="2FA enabled successfully"
        )
    except Exception as e:
        logger.error(f"Error enabling 2FA: {e}")
        return await core_response(
            status_code=500,
            message="Failed to enable 2FA"
        )
