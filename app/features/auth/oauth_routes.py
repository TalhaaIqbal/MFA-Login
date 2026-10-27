from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuthError
from features.auth.oauth_service import oauth
from db.db import get_db_conn
from db.collection import DBCollection
from bson import ObjectId
from time import time
from logging_config import logger
from utils.session_manager import create_session
from utils.core_response import core_response
from config import COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_DOMAIN, COOKIE_PARTITIONED

router = APIRouter()

@router.get("/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    """Start OAuth login flow"""
    if provider not in ['google', 'github', 'microsoft']:
        raise HTTPException(status_code=400, detail="Invalid provider")

    try:
        client = oauth.create_client(provider)
        if not client:
            raise HTTPException(status_code=400, detail=f"{provider} not configured")

        return await client.authorize_redirect(request)
    except Exception as e:
        logger.error(f"OAuth login error for {provider}: {e}")
        raise HTTPException(status_code=500, detail="OAuth login failed")

@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, request: Request):
    """Handle OAuth callback"""
    if provider not in ['google', 'github', 'microsoft']:
        raise HTTPException(status_code=400, detail="Invalid provider")

    try:
        client = oauth.create_client(provider)
        if not client:
            raise HTTPException(status_code=400, detail=f"{provider} not configured")

        token = await client.authorize_access_token(request)
        user_info = await client.parse_id_token(request, token) if provider != 'github' else token

        # Extract user data based on provider
        if provider == 'google':
            email = user_info.get('email')
            name = user_info.get('name')
            provider_id = user_info.get('sub')
        elif provider == 'github':
            user_info = await client.get('user', token=token)
            email = user_info.get('email')
            name = user_info.get('name') or user_info.get('login')
            provider_id = str(user_info.get('id'))
        elif provider == 'microsoft':
            email = user_info.get('email')
            name = user_info.get('name')
            provider_id = user_info.get('sub')

        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")

        # Check if user exists
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

        response = await core_response(
            status_code=200,
            message="OAuth login successful",
            data={
                "user_details": {
                    "id": str(user.get("_id")),
                    "email": user.get("email"),
                    "full_name": user.get("full_name"),
                    "role": user.get("role"),
                    "is_2fa_enabled": user.get("is_2fa_enabled", False),
                }
            }
        )

        # Set cookie
        cookie_kwargs = {
            "httponly": True,
            "secure": COOKIE_SECURE,
            "samesite": COOKIE_SAMESITE,
            "path": "/",
            "max_age": 604800
        }
        if COOKIE_PARTITIONED:
            cookie_kwargs["partitioned"] = True
        if COOKIE_DOMAIN:
            cookie_kwargs["domain"] = COOKIE_DOMAIN

        response.set_cookie(key="session_id", value=session_id, **cookie_kwargs)

        return response

    except OAuthError as e:
        logger.error(f"OAuth error for {provider}: {e}")
        raise HTTPException(status_code=400, detail="OAuth authentication failed")
    except Exception as e:
        logger.error(f"OAuth callback error for {provider}: {e}")
        raise HTTPException(status_code=500, detail="OAuth callback failed")
