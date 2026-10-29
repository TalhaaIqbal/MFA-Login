import asyncio
import sys
from pathlib import Path

# Add parent directory to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from db.db import init_db, get_db_conn
from db.collection import DBCollection
from logging_config import logger


async def create_all_indexes():
    """Create all required indexes for all collections."""
    await init_db()
    db = await get_db_conn()

    # USERS COLLECTION
    users_collection = DBCollection.USERS(db)
    try:
        # Unique index on email - prevents duplicate registrations
        await users_collection.create_index(
            [("email", 1)],
            name="email_unique_idx",
            unique=True
        )
        logger.info("Created unique index on users.email")

        # Index for role filtering
        await users_collection.create_index(
            [("role", 1)],
            name="role_idx"
        )
        logger.info("Created index on users.role")

        # Compound index for admin queries
        await users_collection.create_index(
            [("role", 1), ("email", 1)],
            name="role_email_idx"
        )
        logger.info("Created compound index on (role, email)")

        # Index for 2FA temp token hash - enables O(1) lookup during 2FA verification
        await users_collection.create_index(
            [("_2fa_temp_token_hash", 1)],
            name="temp_token_hash_idx",
            sparse=True
        )
        logger.info("Created sparse index on _2fa_temp_token_hash")

    except Exception as e:
        logger.error(f"Error creating users indexes: {e}")

    # PENDING_EMAIL_VERIFICATIONS COLLECTION
    pending_collection = DBCollection.PENDING_EMAIL_VERIFICATIONS(db)
    try:
        # Unique index on email - prevents duplicate pending verifications
        await pending_collection.create_index(
            [("email", 1)],
            name="pending_email_unique_idx",
            unique=True
        )
        logger.info("Created unique index on pending_email_verifications.email")

        # TTL index for automatic cleanup of expired verifications (24 hours)
        await pending_collection.create_index(
            [("verification_token_expires_at", 1)],
            name="pending_verification_ttl_idx",
            expireAfterSeconds=0
        )
        logger.info("Created TTL index on pending_email_verifications.verification_token_expires_at")

        # Index for cleanup queries
        await pending_collection.create_index(
            [("created_at", 1)],
            name="pending_created_at_idx"
        )
        logger.info("Created index on pending_email_verifications.created_at")

    except Exception as e:
        logger.error(f"Error creating pending_email_verifications indexes: {e}")

    logger.info("All indexes created successfully")


async def create_log_indexes():
    """Legacy function - use create_all_indexes instead."""
    logger.warning("create_log_indexes is deprecated, use create_all_indexes")
    await create_all_indexes()


if __name__ == "__main__":
    asyncio.run(create_all_indexes())
