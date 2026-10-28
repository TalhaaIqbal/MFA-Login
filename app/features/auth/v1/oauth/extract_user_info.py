from fastapi import HTTPException


async def extract_user_info(provider: str, client, token):
    if provider == "google":
        # Fetch userinfo from Google's endpoint
        userinfo = await client.get("https://www.googleapis.com/oauth2/v3/userinfo", token=token)
        info = userinfo.json()
        if not info.get("email_verified", True):
            raise HTTPException(status_code=400, detail="Google email not verified")
        email, name, provider_id = info.get("email"), info.get("name"), info.get("sub")

    elif provider == "github":
        user = (await client.get("user", token=token)).json()
        emails = (await client.get("user/emails", token=token)).json()
        name = user.get("name") or user.get("login")
        provider_id = str(user.get("id"))

        # get the best available email in order of preference:
        # 1. Primary AND verified email
        # 2. Any verified email
        # 3. Any email (even unverified)
        # 4. Placeholder using GitHub username (last resort)
        primary_verified = next((e for e in emails if e.get("primary") and e.get("verified")), None)
        any_verified = next((e for e in emails if e.get("verified")), None)
        any_email = next((e for e in emails if e.get("email")), None)

        if primary_verified:
            email = primary_verified["email"]
        elif any_verified:
            email = any_verified["email"]
        elif any_email:
            email = any_email["email"]
        else:
            # No email at all - generate placeholder using GitHub username
            github_username = user.get("login")
            email = f"{github_username}@github.users.noreply.com"

    elif provider == "microsoft":
        me = (await client.get("me", token=token)).json()
        email = me.get("mail") or me.get("userPrincipalName")
        name = me.get("displayName")
        provider_id = me.get("id")

    else:
        raise HTTPException(status_code=400, detail="Invalid provider")

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")

    return {"email": email.lower(), "name": name, "provider_id": provider_id}
