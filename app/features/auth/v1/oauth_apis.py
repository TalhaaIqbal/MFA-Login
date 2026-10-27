from fastapi import Request, HTTPException
from authlib.integrations.starlette_client import OAuthError
from logging_config import logger
from features.auth.v1.oauth.validate_provider import validate_provider
from features.auth.v1.oauth.get_oauth_client import get_oauth_client
from features.auth.v1.oauth.extract_user_info import extract_user_info
from features.auth.v1.oauth.handle_oauth_user import handle_oauth_user
from features.auth.v1.oauth.set_oauth_cookie import set_oauth_cookie


async def oauth_login_api(provider: str, request: Request):
    validate_provider(provider)

    try:
        client = get_oauth_client(provider)
        return await client.authorize_redirect(request)
    except Exception as e:
        logger.error(f"OAuth login error for {provider}: {e}")
        raise HTTPException(status_code=500, detail="OAuth login failed")




async def oauth_callback_api(provider: str, request: Request):
    validate_provider(provider)

    try:
        client = get_oauth_client(provider)
        token = await client.authorize_access_token(request)

        # Extract user data
        user_data = await extract_user_info(provider, client, token, request)

        # Handle user (login or signup)
        session_id, user = await handle_oauth_user(
            user_data["email"],
            user_data["name"],
            provider,
            user_data["provider_id"]
        )

        # Set cookie and redirect
        return set_oauth_cookie(session_id)

    except OAuthError as e:
        logger.error(f"OAuth error for {provider}: {e}")
        raise HTTPException(status_code=400, detail="OAuth authentication failed")
    except Exception as e:
        logger.error(f"OAuth callback error for {provider}: {e}")
        raise HTTPException(status_code=500, detail="OAuth callback failed")
