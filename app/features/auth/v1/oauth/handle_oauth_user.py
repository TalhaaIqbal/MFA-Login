from db.db import get_db_conn
from db.collection import DBCollection
from time import time
from logging_config import logger
from utils.session_manager import create_session


async def handle_oauth_user(email: str, name: str, provider: str, provider_id: str):
    """Handle OAuth user - login existing or create new user"""
    db_conn = await get_db_conn()
    users_collection = DBCollection.USERS(db_conn)

    user = await users_collection.find_one({"email": email})

    if user:
        # Existing user - login
        session_id = await create_session(str(user.get("_id")))
        logger.info(f"OAuth login successful for user ID: {user.get('_id')}")
    else:
        # New user - signup
        new_user = {
            "email": email,
            "full_name": name or email.split('@')[0],
            "role": "user",
            "is_2fa_enabled": False,
            "oauth_provider": provider,
            "oauth_provider_id": provider_id,
            "created_at": int(time() * 1000),
            "updated_at": int(time() * 1000)
        }
        result = await users_collection.insert_one(new_user)
        session_id = await create_session(str(result.inserted_id))
        logger.info(f"OAuth signup successful for user ID: {result.inserted_id}")

    # Get user details
    user = await users_collection.find_one({"email": email})

    return session_id, user
