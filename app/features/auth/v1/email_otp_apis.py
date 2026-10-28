from .email_otp.setup_email_otp import setup_email_otp
from .email_otp.enable_email_otp import enable_email_otp
from .email_otp.disable_email_otp import disable_email_otp
from .email_otp.verify_email_otp import verify_email_otp_login


async def setup_email_otp_api(user_id: str, email: str):
    return await setup_email_otp(user_id, email)


async def enable_email_otp_api(user_id: str, code: str):
    return await enable_email_otp(user_id, code)


async def disable_email_otp_api(user_id: str, password: str = None):
    return await disable_email_otp(user_id, password)


async def verify_email_otp_api(temp_token: str, code: str):
    return await verify_email_otp_login(temp_token, code)


__all__ = ['setup_email_otp_api', 'enable_email_otp_api', 'disable_email_otp_api', 'verify_email_otp_api']
