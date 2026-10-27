# Path: features/auth/v1/auth/signup.py
import traceback
from time import time
from db.db import get_db_conn
from db.collection import DBCollection
from logging_config import logger
from models.auth.auth import RegisterRequest
from features.auth.utils.hash_password import hash_password
from utils.session_manager import create_session
from utils.core_response import core_response
from config import COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_DOMAIN


async def signup(payload: RegisterRequest):
    logger.info(f"Signing up new user: {payload.email}")
    try:
        db_conn = await get_db_conn()
        user_collection = DBCollection.USERS(db_conn)

        # Check if user already exists
        existing_user = await user_collection.find_one(
            {"email": payload.email},
            {}
        )

        if existing_user:
            logger.warning(f"User already exists: {payload.email}")
            return await core_response(
                status_code=400,
                message="Email already registered"
            )

        # Hash the password
        hashed_password = hash_password(payload.password)

        now = int(time() * 1000)

        # Create new user
        new_user = {
            "email": payload.email,
            "password": hashed_password,
            "full_name": payload.name,
            "role": "user",  # Default role for new signups
            "is_2fa_enabled": False,
            "created_at": now,
            "updated_at": now
        }

        result = await user_collection.insert_one(new_user)

        # Create session for automatic login after signup
        session_id = await create_session(str(result.inserted_id))

        response = await core_response(
            status_code=201,
            message="User registered successfully",
            data={
                "user_details": {
                    "id": str(result.inserted_id),
                    "email": payload.email,
                    "full_name": payload.name,
                    "role": "user"
                }
            }
        )

        # Set HttpOnly cookie for session
        cookie_kwargs = {
            "httponly": True,
            "secure": COOKIE_SECURE,
            "samesite": COOKIE_SAMESITE,
            "path": "/",
            "max_age": 1800  # 30 minutes
        }
        if COOKIE_DOMAIN:
            cookie_kwargs["domain"] = COOKIE_DOMAIN

        response.set_cookie(
            key="session_id",
            value=session_id,
            **cookie_kwargs
        )

        return response

    except Exception as e:
        logger.error(f"Error: {e}\n{traceback.format_exc()}")
        return await core_response(
            status_code=500,
            message="Internal server error"
        )