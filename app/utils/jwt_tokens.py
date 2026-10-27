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
