from datetime import datetime, timezone, timedelta
from bson import ObjectId
from db.db import get_db_conn
from db.collection import DBCollection
from logging_config import logger
import secrets
import hashlib


async def create_challenge(user_id: str, challenge_type: str, challenge_data: str, expires_in_minutes: int = 10):
    """Create an authentication challenge (OTP, setup token, etc.)"""
    try:
        db_conn = await get_db_conn()
        challenges_collection = DBCollection.AUTH_CHALLENGES(db_conn)

        challenge_id = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

        # Hash the challenge ID for secure lookup
        challenge_id_hash = hashlib.sha256(challenge_id.encode()).hexdigest()

        await challenges_collection.insert_one({
            "challenge_id_hash": challenge_id_hash,
            "user_id": ObjectId(user_id),
            "challenge_type": challenge_type,
            "challenge_data": challenge_data,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.now(timezone.utc)
        })

        logger.info(f"Created {challenge_type} challenge for user {user_id}")
        return challenge_id
    except Exception as e:
        logger.error(f"Error creating challenge: {e}")
        raise


async def verify_and_consume_challenge(challenge_id: str, challenge_type: str, provided_data: str = None):
    """Verify a challenge and mark it as used"""
    try:
        db_conn = await get_db_conn()
        challenges_collection = DBCollection.AUTH_CHALLENGES(db_conn)

        # Hash the challenge ID for lookup
        challenge_id_hash = hashlib.sha256(challenge_id.encode()).hexdigest()

        # Find unused challenge
        challenge = await challenges_collection.find_one({
            "challenge_id_hash": challenge_id_hash,
            "challenge_type": challenge_type,
            "used": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })

        if not challenge:
            logger.warning(f"Invalid or expired challenge: {challenge_id}")
            return None

        # Verify the challenge data if provided
        if provided_data and challenge["challenge_data"] != provided_data:
            logger.warning(f"Invalid challenge data for user {challenge['user_id']}")
            return None

        # Mark as used
        await challenges_collection.update_one(
            {"_id": challenge["_id"]},
            {"$set": {"used": True, "used_at": datetime.now(timezone.utc)}}
        )

        logger.info(f"Verified and consumed {challenge_type} challenge for user {challenge['user_id']}")
        return str(challenge["user_id"])
    except Exception as e:
        logger.error(f"Error verifying challenge: {e}")
        return None


async def get_challenge_data(challenge_id: str, challenge_type: str):
    """Get challenge data without consuming it (for verification)"""
    try:
        db_conn = await get_db_conn()
        challenges_collection = DBCollection.AUTH_CHALLENGES(db_conn)

        challenge_id_hash = hashlib.sha256(challenge_id.encode()).hexdigest()

        challenge = await challenges_collection.find_one({
            "challenge_id_hash": challenge_id_hash,
            "challenge_type": challenge_type,
            "used": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })

        if challenge:
            return {
                "user_id": str(challenge["user_id"]),
                "challenge_data": challenge["challenge_data"],
                "expires_at": challenge["expires_at"]
            }
        return None
    except Exception as e:
        logger.error(f"Error getting challenge data: {e}")
        return None


async def delete_user_challenges(user_id: str, challenge_type: str = None):
    """Delete all challenges for a user (optionally filtered by type)"""
    try:
        db_conn = await get_db_conn()
        challenges_collection = DBCollection.AUTH_CHALLENGES(db_conn)

        query = {"user_id": ObjectId(user_id)}
        if challenge_type:
            query["challenge_type"] = challenge_type

        result = await challenges_collection.delete_many(query)
        logger.info(f"Deleted {result.deleted_count} challenges for user {user_id}")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error deleting challenges: {e}")
        return 0


async def cleanup_expired_challenges():
    """Clean up expired challenges from the database"""
    try:
        db_conn = await get_db_conn()
        challenges_collection = DBCollection.AUTH_CHALLENGES(db_conn)

        now = datetime.now(timezone.utc)
        result = await challenges_collection.delete_many({
            "expires_at": {"$lt": now}
        })

        logger.info(f"Cleaned up {result.deleted_count} expired challenges")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up expired challenges: {e}")
        return 0
