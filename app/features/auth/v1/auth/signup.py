# Path: features/auth/v1/auth/signup.py
import traceback
from logging_config import logger
from models.auth.auth import RegisterRequest
from features.auth.v1.auth.email_verification import initiate_email_verification
from utils.core_response import core_response


async def signup(payload: RegisterRequest):
    logger.info(f"Initiating signup for: {payload.email}")
    try:
        # Normalize email to lowercase
        email = payload.email.lower()

        # Initiate email verification flow
        result = await initiate_email_verification(email, payload.name, payload.password)

        return result

    except Exception as e:
        logger.error(f"Error: {e}\n{traceback.format_exc()}")
        return await core_response(
            status_code=500,
            message="Internal server error"
        )