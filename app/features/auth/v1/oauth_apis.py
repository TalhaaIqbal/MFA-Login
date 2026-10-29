from fastapi import Request, Response
from authlib.integrations.starlette_client import OAuthError
from logging_config import logger
from config import FRONTEND_URL, GOOGLE_REDIRECT_URI, GITHUB_REDIRECT_URI, MICROSOFT_REDIRECT_URI
from features.auth.v1.oauth.validate_provider import validate_provider
from features.auth.v1.oauth.get_oauth_client import get_oauth_client
from features.auth.v1.oauth.extract_user_info import extract_user_info
from features.auth.v1.oauth.handle_oauth_user import handle_oauth_user
from features.auth.v1.oauth.set_oauth_cookie import set_oauth_cookie

REDIRECT_URIS = {
    "google": GOOGLE_REDIRECT_URI,
    "github": GITHUB_REDIRECT_URI,
    "microsoft": MICROSOFT_REDIRECT_URI,
}


def _login_error(code: str):
    return Response(status_code=302, headers={"Location": f"{FRONTEND_URL}/login?error={code}"})


async def oauth_login_api(provider: str, request: Request, prompt: str = None):
    validate_provider(provider)
    client = get_oauth_client(provider)
    redirect_uri = REDIRECT_URIS[provider] or str(request.url_for("oauth_callback", provider=provider))

    # Add prompt parameter if provided (e.g., "login" to force account selection)
    if prompt:
        return await client.authorize_redirect(request, redirect_uri, prompt=prompt)
    return await client.authorize_redirect(request, redirect_uri)


async def oauth_callback_api(provider: str, request: Request):
    validate_provider(provider)
    try:
        client = get_oauth_client(provider)
        token = await client.authorize_access_token(request)
        user = await extract_user_info(provider, client, token)
        session_id, user_data, mfa_data = await handle_oauth_user(user["email"], user["name"], provider, user["provider_id"])

        # If 2FA is required, redirect to frontend with MFA data
        if mfa_data:
            from json import dumps
            # Pass MFA data as query params
            mfa_params = f"?requires_2fa=true&mfa_method={mfa_data['mfa_method']}&temp_token={mfa_data['temp_token']}&user_id={mfa_data['user_id']}"
            return Response(status_code=302, headers={"Location": f"{FRONTEND_URL}/oauth/callback{mfa_params}"})

        logger.info("Session id: %s, use data: %s, mfa data: %s", session_id, user_data, mfa_data)
        return set_oauth_cookie(session_id)
    except OAuthError as e:
        logger.error(f"OAuth error for {provider}: {e}")
        return _login_error("oauth_failed")
    except Exception as e:
        logger.error(f"OAuth callback error for {provider}: {e}")
        return _login_error("oauth_failed")
