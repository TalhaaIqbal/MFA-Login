from fastapi import HTTPException


def validate_provider(provider: str):
    valid_providers = ['google', 'github', 'microsoft']
    if provider not in valid_providers:
        raise HTTPException(status_code=400, detail="Invalid provider")
    return provider
