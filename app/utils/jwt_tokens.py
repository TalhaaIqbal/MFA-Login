import jwt
from datetime import datetime, timedelta, timezone
from config import ENCRYPTION_KEY
from logging_config import logger


def create_temp_token(user_id: str, token_type: str, expires_in_minutes: int = 5) -> str:
    """Create a temporary JWT token for 2FA or OAuth flow"""
    try:
        payload = {
            "user_id": user_id,
            "type": token_type,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),
            "iat": datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, ENCRYPTION_KEY, algorithm="HS256")
        logger.info(f"Created {token_type} token for user {user_id}")
        return token
    except Exception as e:
        logger.error(f"Error creating temp token: {e}")
        raise


def verify_temp_token(token: str, token_type: str) -> dict | None:
    """Verify a temporary JWT token and return user_id"""
    try:
        payload = jwt.decode(token, ENCRYPTION_KEY, algorithms=["HS256"])
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: {payload.get('type')} != {token_type}")
            return None
        return {"user_id": payload.get("user_id")}
    except jwt.ExpiredSignatureError:
        logger.warning("Temp token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid temp token: {e}")
        return None


def create_email_verification_token(email: str, expires_in_hours: int = 24) -> str:
    """Create a JWT token for email verification"""
    try:
        payload = {
            "email": email,
            "type": "email_verification",
            "exp": datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
            "iat": datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, ENCRYPTION_KEY, algorithm="HS256")
        logger.info(f"Created email verification token for {email}")
        return token
    except Exception as e:
        logger.error(f"Error creating email verification token: {e}")
        raise


def verify_email_verification_token(token: str) -> dict | None:
    """Verify an email verification token and return email"""
    try:
        payload = jwt.decode(token, ENCRYPTION_KEY, algorithms=["HS256"])
        if payload.get("type") != "email_verification":
            logger.warning(f"Invalid token type: {payload.get('type')} != email_verification")
            return None
        return {"email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        logger.warning("Email verification token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid email verification token: {e}")
        return None
