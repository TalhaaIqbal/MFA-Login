from db.db import get_db_conn
from db.collection import DBCollection
from time import time
from logging_config import logger
from utils.session_manager import create_session
from utils.jwt_tokens import create_temp_token
from bson import ObjectId


async def handle_oauth_user(email: str, name: str, provider: str, provider_id: str):
    db_conn = await get_db_conn()
    users_collection = DBCollection.USERS(db_conn)

    # Check if user exists with this OAuth provider
    user = await users_collection.find_one({
        "oauth_providers": {
            "$elemMatch": {
                "provider": provider,
                "provider_id": provider_id
            }
        }
    })

    if user:
        # Existing user via OAuth - login
        user_id = str(user.get("_id"))
        # Update last used timestamp
        await users_collection.update_one(
            {"_id": ObjectId(user_id), "oauth_providers.provider": provider},
            {"$set": {"oauth_providers.$.last_used": int(time() * 1000)}}
        )
        logger.info(f"OAuth login successful for user ID: {user_id}")
    else:
        # Check if user exists by email (but not via this OAuth provider)
        user = await users_collection.find_one({"email": email})

        if user:
            # Existing user with email, but new OAuth provider - link it
            user_id = str(user.get("_id"))
            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$push": {
                        "oauth_providers": {
                            "provider": provider,
                            "provider_id": provider_id,
                            "email": email,
                            "created_at": int(time() * 1000),
                            "last_used": int(time() * 1000)
                        }
                    }
                }
            )
            logger.info(f"OAuth provider linked for user ID: {user_id}")
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
        else:
            # New user - signup
            new_user = {
                "email": email,
                "full_name": name or email.split('@')[0],
                "role": "user",
                "is_2fa_enabled": False,
                "oauth_providers": [{
                    "provider": provider,
                    "provider_id": provider_id,
                    "email": email,
                    "created_at": int(time() * 1000),
                    "last_used": int(time() * 1000)
                }],
                "created_at": int(time() * 1000),
                "updated_at": int(time() * 1000)
            }
            result = await users_collection.insert_one(new_user)
            user_id = str(result.inserted_id)
            logger.info(f"OAuth signup successful for user ID: {user_id}")
            user = await users_collection.find_one({"_id": ObjectId(user_id)})

    # Check if 2FA is enabled
    is_2fa_enabled = user.get("is_2fa_enabled", False)
    is_email_otp_enabled = user.get("is_email_otp_enabled", False)

    if is_2fa_enabled:
        # Create JWT token for TOTP 2FA verification
        temp_token = create_temp_token(
            user_id=str(user.get("_id")),
            token_type="totp_login",
            expires_in_minutes=5
        )
        logger.info(f"TOTP 2FA required for OAuth user ID: {user.get('_id')}")
        return None, user, {"requires_2fa": True, "mfa_method": "totp", "temp_token": temp_token, "user_id": str(user.get("_id"))}

    if is_email_otp_enabled:
        # Generate and send email OTP
        from utils.email_otp import generate_otp, send_email_otp
        otp = generate_otp()
        await send_email_otp(user.get("email"), otp, expiry_minutes=2)

        # Store OTP and expiry timestamp (2 minutes) in user document
        expiry_time = int(time()) + 120  # 2 minutes = 120 seconds
        await users_collection.update_one(
            {"_id": user.get("_id")},
            {"$set": {"email_otp": otp, "email_otp_expiry": expiry_time}}
        )

        # Create JWT token for email OTP verification
        temp_token = create_temp_token(
            user_id=str(user.get("_id")),
            token_type="email_otp_login",
            expires_in_minutes=10
        )
        logger.info(f"Email OTP required for OAuth user ID: {user.get('_id')}")
        return None, user, {"requires_2fa": True, "mfa_method": "email", "temp_token": temp_token, "user_id": str(user.get("_id"))}

    # No 2FA - create session
    session_id = await create_session(str(user.get("_id")))
    logger.info(f"OAuth session created for user ID: {user.get('_id')}")

    return session_id, user, None
