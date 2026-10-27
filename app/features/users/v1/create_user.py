# Path: features/users/v1/create_user.py
from db.db import get_db_conn
from db.collection import DBCollection
from logging_config import logger
from utils.core_response import core_response
from features.auth.utils.hash_password import hash_password


async def create_user(user_data: dict):
    try:
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        logger.info(f"Creating user with email: {user_data.get('email')}")

        # Check if user already exists
        existing_user = await users_collection.find_one({"email": user_data.get("email")})
        if existing_user:
            return await core_response(
                status_code=400,
                message="User with this email already exists"
            )

        # Hash password if provided
        if "password" in user_data:
            user_data["password"] = hash_password(user_data["password"])

        # Insert new user
        result = await users_collection.insert_one(user_data)

        logger.info(f"User created with ID: {result.inserted_id}")

        # Get the created user
        created_user = await users_collection.find_one(
            {"_id": result.inserted_id},
            {
                "password": 0,
                "_2fa_secret": 0,
                "_2fa_temp_token": 0,
                "_2fa_temp_token_expires": 0
            }
        )

        return await core_response(
            status_code=201,
            message="User created successfully",
            data=created_user
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise
