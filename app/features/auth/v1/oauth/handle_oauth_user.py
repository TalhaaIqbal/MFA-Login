from db.db import get_db_conn
from db.collection import DBCollection
from time import time
from logging_config import logger
from utils.session_manager import create_session
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
        session_id = await create_session(user_id)
        # Update last used timestamp
        await users_collection.update_one(
            {"_id": ObjectId(user_id), "oauth_providers.provider": provider},
            {"$set": {"oauth_providers.$.last_used": int(time() * 1000)}}
        )
        logger.info(f"OAuth login successful for user ID: {user_id}")
        return session_id, user

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
        session_id = await create_session(user_id)
        logger.info(f"OAuth provider linked for user ID: {user_id}")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        return session_id, user
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
        session_id = await create_session(user_id)
        logger.info(f"OAuth signup successful for user ID: {user_id}")

    # Get user details
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    return session_id, user
