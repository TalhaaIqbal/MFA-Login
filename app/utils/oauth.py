from authlib.integrations.starlette_client import OAuth
from config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
    MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT_ID,
)

oauth = OAuth()


def init_oauth(app):
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        oauth.register(
            name="google",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
        oauth.register(
            name="github",
            client_id=GITHUB_CLIENT_ID,
            client_secret=GITHUB_CLIENT_SECRET,
            authorize_url="https://github.com/login/oauth/authorize",
            access_token_url="https://github.com/login/oauth/access_token",
            api_base_url="https://api.github.com/",
            client_kwargs={"scope": "read:user user:email"},
        )

    # Plain OAuth + Graph /me instead of OIDC: id_token issuer validation fails on the "common" tenant
    if MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET:
        tenant = MICROSOFT_TENANT_ID or "common"
        oauth.register(
            name="microsoft",
            client_id=MICROSOFT_CLIENT_ID,
            client_secret=MICROSOFT_CLIENT_SECRET,
            authorize_url=f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
            access_token_url=f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
            api_base_url="https://graph.microsoft.com/v1.0/",
            client_kwargs={"scope": "User.Read"},
        )
