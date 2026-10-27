from db.db import get_db_conn
from db.collection import DBCollection
from time import time
from logging_config import logger
from utils.session_manager import create_session
from utils.auth_identities import create_oauth_identity, find_user_by_oauth_identity
from bson import ObjectId


async def handle_oauth_user(email: str, name: str, provider: str, provider_id: str):
    db_conn = await get_db_conn()
    users_collection = DBCollection.USERS(db_conn)

    # First check if OAuth identity exists
    user_id = await find_user_by_oauth_identity(provider, provider_id)

    if user_id:
        # Existing user via OAuth identity - login
        session_id = await create_session(user_id)
        # Update last used timestamp
        await create_oauth_identity(user_id, provider, provider_id, email)
        logger.info(f"OAuth login successful for user ID: {user_id}")
        return session_id

    # Check if user exists by email (but not via this OAuth provider)
    user = await users_collection.find_one({"email": email})

    if user:
        # Existing user with email, but new OAuth provider - link it
        await create_oauth_identity(str(user.get("_id")), provider, provider_id, email)
        session_id = await create_session(str(user.get("_id")))
        logger.info(f"OAuth provider linked for user ID: {user.get('_id')}")
        return session_id
    else:
        # New user - signup
        new_user = {
            "email": email,
            "full_name": name or email.split('@')[0],
            "role": "user",
            "is_2fa_enabled": False,
            "created_at": int(time() * 1000),
            "updated_at": int(time() * 1000)
        }
        result = await users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        # Create OAuth identity
        await create_oauth_identity(user_id, provider, provider_id, email)
        session_id = await create_session(user_id)
        logger.info(f"OAuth signup successful for user ID: {user_id}")

    # Get user details
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    return session_id, user
