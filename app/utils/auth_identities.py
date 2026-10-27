from datetime import datetime, timezone
from bson import ObjectId
from db.db import get_db_conn
from db.collection import DBCollection
from logging_config import logger


async def create_oauth_identity(user_id: str, provider: str, provider_id: str, email: str):
    """Create or update an OAuth identity for a user"""
    try:
        db_conn = await get_db_conn()
        identities_collection = DBCollection.AUTH_IDENTITIES(db_conn)

        # Check if identity already exists
        existing = await identities_collection.find_one({
            "provider": provider,
            "provider_id": provider_id
        })

        if existing:
            # Update last used
            await identities_collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {"last_used": datetime.now(timezone.utc)}}
            )
            logger.info(f"Updated OAuth identity for user {user_id}, provider {provider}")
            return str(existing["_id"])
        else:
            # Create new identity
            result = await identities_collection.insert_one({
                "user_id": ObjectId(user_id),
                "provider": provider,
                "provider_id": provider_id,
                "email": email,
                "created_at": datetime.now(timezone.utc),
                "last_used": datetime.now(timezone.utc)
            })
            logger.info(f"Created OAuth identity for user {user_id}, provider {provider}")
            return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating OAuth identity: {e}")
        raise


async def get_user_identities(user_id: str):
    """Get all OAuth identities for a user"""
    try:
        db_conn = await get_db_conn()
        identities_collection = DBCollection.AUTH_IDENTITIES(db_conn)

        cursor = identities_collection.find({"user_id": ObjectId(user_id)})
        identities = []
        async for identity in cursor:
            identities.append({
                "id": str(identity["_id"]),
                "provider": identity["provider"],
                "provider_id": identity["provider_id"],
                "email": identity["email"],
                "created_at": identity["created_at"],
                "last_used": identity["last_used"]
            })
        return identities
    except Exception as e:
        logger.error(f"Error getting user identities: {e}")
        return []


async def find_user_by_oauth_identity(provider: str, provider_id: str):
    """Find a user by OAuth identity"""
    try:
        db_conn = await get_db_conn()
        identities_collection = DBCollection.AUTH_IDENTITIES(db_conn)

        identity = await identities_collection.find_one({
            "provider": provider,
            "provider_id": provider_id
        })

        if identity:
            return str(identity["user_id"])
        return None
    except Exception as e:
        logger.error(f"Error finding user by OAuth identity: {e}")
        return None


async def delete_oauth_identity(user_id: str, provider: str):
    """Delete an OAuth identity for a user"""
    try:
        db_conn = await get_db_conn()
        identities_collection = DBCollection.AUTH_IDENTITIES(db_conn)

        result = await identities_collection.delete_one({
            "user_id": ObjectId(user_id),
            "provider": provider
        })

        if result.deleted_count > 0:
            logger.info(f"Deleted OAuth identity for user {user_id}, provider {provider}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting OAuth identity: {e}")
        return False
