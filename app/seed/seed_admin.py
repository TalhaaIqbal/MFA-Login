import asyncio
import sys
from pathlib import Path
from time import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.db import get_db_conn, init_db, close_db_conn
from db.collection import DBCollection
from features.auth.utils.hash_password import hash_password
from logging_config import logger
from config import ADMIN_EMAIL, ADMIN_PASSWORD


async def seed_admin_user():
    """Seed the admin user into the database"""
    try:
        await init_db()
        db_conn = await get_db_conn()
        users_collection = DBCollection.USERS(db_conn)

        if not ADMIN_EMAIL or not ADMIN_PASSWORD:
            logger.error("ADMIN_EMAIL and ADMIN_PASSWORD must be set in environment")
            logger.error("Skipping admin user seeding. Set these environment variables and run again.")
            return

        logger.info(f"Checking if admin user exists: {ADMIN_EMAIL}")

        existing_user = await users_collection.find_one({"email": ADMIN_EMAIL})
        if existing_user:
            logger.info("Admin user already exists. Skipping seed.")
            logger.info(f"Existing user ID: {existing_user.get('_id')}")
            return

        logger.info("Creating admin user...")

        admin_user = {
            "email": ADMIN_EMAIL,
            "full_name": "Admin",
            "role": "admin",
            "password": hash_password(ADMIN_PASSWORD),
            "created_at": int(time() * 1000),
            "updated_at": int(time() * 1000)
        }

        result = await users_collection.insert_one(admin_user)
        logger.info(f"Admin user created successfully with ID: {result.inserted_id}")

        created_user = await users_collection.find_one(
            {"_id": result.inserted_id},
            {"password": 0}
        )
        logger.info(f"Created user: {created_user}")

    except Exception as e:
        logger.error(f"Error seeding admin user: {e}")
        raise
    finally:
        await close_db_conn()


if __name__ == "__main__":
    asyncio.run(seed_admin_user())
