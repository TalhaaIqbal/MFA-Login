from authlib.integrations.starlette_client import OAuth
from config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI,
    MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT_ID, MICROSOFT_REDIRECT_URI
)

oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth providers with the FastAPI app"""
    # Register Google
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        oauth.register(
            name='google',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
            redirect_uri=GOOGLE_REDIRECT_URI
        )

    # Register GitHub
    if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
        oauth.register(
            name='github',
            client_id=GITHUB_CLIENT_ID,
            client_secret=GITHUB_CLIENT_SECRET,
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'},
            redirect_uri=GITHUB_REDIRECT_URI
        )

    # Register Microsoft
    if MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET:
        oauth.register(
            name='microsoft',
            client_id=MICROSOFT_CLIENT_ID,
            client_secret=MICROSOFT_CLIENT_SECRET,
            server_metadata_url=f'https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/v2.0/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
            redirect_uri=MICROSOFT_REDIRECT_URI
        )

