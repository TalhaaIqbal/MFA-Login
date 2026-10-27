from .two_fa.setup_2fa import setup_2fa
from .two_fa.enable_2fa import enable_2fa
from .two_fa.disable_2fa import disable_2fa
from .two_fa.verify_2fa import verify_2fa_login


async def setup_2fa_api(user_id: str, email: str):
    return await setup_2fa(user_id, email)


async def enable_2fa_api(user_id: str, code: str, challenge_id: str = None):
    return await enable_2fa(user_id, code)


async def disable_2fa_api(user_id: str, password: str = None, totp_code: str = None):
    return await disable_2fa(user_id, password, totp_code)


async def verify_2fa_api(temp_token: str, code: str):
    return await verify_2fa_login(temp_token, code)


__all__ = ['setup_2fa_api', 'enable_2fa_api', 'disable_2fa_api', 'verify_2fa_api']

