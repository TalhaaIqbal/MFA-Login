import secrets
from datetime import datetime, timezone, timedelta
from time import time
from bson import ObjectId
from db.db import get_db_conn
from db.collection import DBCollection
from logging_config import logger
from config import MAX_AGE


async def create_session(user_id: str, expires_delta: timedelta | None = None) -> str:

    try:
        db_conn = await get_db_conn()
        sessions_collection = DBCollection.AUTH_SESSIONS(db_conn)

        # Generate secure random session ID
        session_id = secrets.token_urlsafe(32)

        # Set expiration time as Unix timestamp in milliseconds (use MAX_AGE by default)
        if expires_delta:
            expires_at = int((datetime.now(timezone.utc) + expires_delta).timestamp() * 1000)
        else:
            # Use MAX_AGE from config (in seconds, convert to milliseconds)
            expires_at = int(time() * 1000) + (MAX_AGE * 1000)

        # Store session in database
        await sessions_collection.insert_one({
            "session_id": session_id,
            "user_id": ObjectId(user_id),
            "created_at": int(time() * 1000),
            "expires_at": expires_at,
            "revoked": False
        })

        logger.info(f"Created session {session_id} for user_id={user_id}")
        return session_id
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise


async def verify_session(session_id: str) -> dict | None:

    try:
        db_conn = await get_db_conn()
        sessions_collection = DBCollection.AUTH_SESSIONS(db_conn)
        users_collection = DBCollection.USERS(db_conn)

        # Find session with projection to reduce data transfer
        session = await sessions_collection.find_one(
            {"session_id": session_id},
            {"_id": 0, "user_id": 1, "expires_at": 1, "revoked": 1}
        )

        if not session:
            logger.warning(f"Session not found: {session_id}")
            return None

        # Check if session is revoked
        if session.get("revoked", False):
            logger.warning(f"Session revoked: {session_id}")
            return None

        # Check if session is expired (using Unix timestamp in milliseconds)
        expires_at = session.get("expires_at")
        if expires_at:
            current_time = int(time() * 1000)
            if expires_at < current_time:
                logger.warning(f"Session expired: {session_id}")
                # Clean up expired session
                await sessions_collection.delete_one({"session_id": session_id})
                return None
        else:
            logger.warning(f"Session has no expiration: {session_id}")
            return None

        # Get user data with projection
        user_id = session.get("user_id")
        user_doc = await users_collection.find_one(
            {"_id": user_id},
            {"email": 1, "full_name": 1, "role": 1, "is_2fa_enabled": 1, "is_email_otp_enabled": 1}
        )

        if not user_doc:
            logger.warning(f"User not found for session: {session_id}")
            return None

        return {
            "id": str(user_id),
            "email": user_doc.get("email"),
            "full_name": user_doc.get("full_name"),
            "role": user_doc.get("role", "user"),
            "is_2fa_enabled": user_doc.get("is_2fa_enabled", False),
            "is_email_otp_enabled": user_doc.get("is_email_otp_enabled", False),
        }
    except Exception as e:
        logger.error(f"Error verifying session: {e}")
        return None


async def revoke_session(session_id: str) -> bool:

    try:
        db_conn = await get_db_conn()
        sessions_collection = DBCollection.AUTH_SESSIONS(db_conn)

        result = await sessions_collection.update_one(
            {"session_id": session_id, "revoked": False},
            {"$set": {"revoked": True, "revoked_at": int(time() * 1000)}}
        )

        if result.modified_count > 0:
            logger.info(f"Revoked session {session_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error revoking session: {e}")
        return False


async def revoke_all_user_sessions(user_id: str) -> int:

    try:
        db_conn = await get_db_conn()
        sessions_collection = DBCollection.AUTH_SESSIONS(db_conn)

        result = await sessions_collection.update_many(
            {"user_id": ObjectId(user_id), "revoked": False},
            {"$set": {"revoked": True, "revoked_at": int(time() * 1000)}}
        )

        logger.info(f"Revoked {result.modified_count} sessions for user_id={user_id}")
        return result.modified_count
    except Exception as e:
        logger.error(f"Error revoking all user sessions: {e}")
        return 0


async def cleanup_expired_sessions():

    try:
        db_conn = await get_db_conn()
        sessions_collection = DBCollection.AUTH_SESSIONS(db_conn)

        now = int(time() * 1000)
        result = await sessions_collection.delete_many({
            "expires_at": {"$lt": now}
        })

        logger.info(f"Cleaned up {result.deleted_count} expired sessions")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        return 0
