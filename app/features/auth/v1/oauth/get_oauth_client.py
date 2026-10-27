from fastapi import HTTPException
from utils.oauth import oauth


def get_oauth_client(provider: str):
    client = oauth.create_client(provider)
    if not client:  
        raise HTTPException(status_code=400, detail=f"{provider} not configured")
    return client
