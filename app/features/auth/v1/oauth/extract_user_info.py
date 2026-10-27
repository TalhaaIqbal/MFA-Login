from fastapi import HTTPException


async def extract_user_info(provider: str, client, token, request):
    """Extract user information from OAuth provider"""
    if provider == 'google':
        user_info = await client.parse_id_token(request, token)
        email = user_info.get('email')
        name = user_info.get('name')
        provider_id = user_info.get('sub')
    elif provider == 'github':
        user_info = await client.get('user', token=token)
        email = user_info.get('email')
        name = user_info.get('name') or user_info.get('login')
        provider_id = str(user_info.get('id'))
    elif provider == 'microsoft':
        user_info = await client.parse_id_token(request, token)
        email = user_info.get('email')
        name = user_info.get('name')
        provider_id = user_info.get('sub')
    else:
        raise HTTPException(status_code=400, detail="Invalid provider")

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")

    return {
        "email": email,
        "name": name,
        "provider_id": provider_id
    }
