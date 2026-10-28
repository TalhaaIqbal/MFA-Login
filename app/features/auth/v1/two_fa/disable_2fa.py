from db.db import get_db_conn
from db.collection import DBCollection
from utils.core_response import core_response
from bson import ObjectId
from logging_config import logger
from features.auth.utils.verify_password import verify_password
from features.auth.utils.two_factor import verify_totp_code
from utils.encryption import decrypt_data


async def disable_2fa(user_id: str, password: str = None, totp_code: str = None):
    """Disable 2FA for the current user with step-up authentication"""
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return await core_response(
                status_code=404,
                message="User not found"
            )

        # Guard check: if 2FA is already disabled (both methods)
        if user.get("is_2fa_enabled") is not True and user.get("is_email_otp_enabled") is not True:
            return await core_response(
                status_code=400,
                message="2FA is already disabled"
            )
        

        # Step-up authentication: require either password OR TOTP code
        if not password and not totp_code:
            return await core_response(
                status_code=400,
                message="Step-up authentication required: provide either password or TOTP code"
            )

        # Verify password if provided
        if password:
            if not verify_password(password, user.get("password")):
                logger.warning(f"Invalid password for 2FA disable attempt by user {user_id}")
                return await core_response(
                    status_code=401,
                    message="Invalid password"
                )

        # Verify TOTP code if provided
        if totp_code:
            try:
                decrypted_secret = decrypt_data(user["_2fa_secret"])
            except ValueError:
                return await core_response(
                    status_code=500,
                    message="Failed to decrypt 2FA secret"
                )

            if not verify_totp_code(decrypted_secret, totp_code):
                logger.warning(f"Invalid TOTP code for 2FA disable attempt by user {user_id}")
                return await core_response(
                    status_code=401,
                    message="Invalid TOTP code"
                )

        # Disable 2FA (both TOTP and email OTP)
        unset_fields = {}
        if user.get("is_2fa_enabled") is True:
            unset_fields["is_2fa_enabled"] = 1
            unset_fields["_2fa_secret"] = 1
        if user.get("is_email_otp_enabled") is True:
            unset_fields["is_email_otp_enabled"] = 1

        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$unset": unset_fields}
        )

        logger.info(f"2FA disabled successfully for user {user_id} with step-up authentication")

        return await core_response(
            status_code=200,
            message="2FA disabled successfully"
        )
    except Exception as e:
        logger.error(f"Error disabling 2FA: {e}")
        return await core_response(
            status_code=500,
            message="Failed to disable 2FA"
        )
