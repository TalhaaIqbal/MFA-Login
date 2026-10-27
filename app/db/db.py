import asyncio
import certifi
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from config import (
    DB_URI,
    MONGO_DB
)

_client:  AsyncMongoClient | None = None
_db: AsyncDatabase | None = None
_lock = asyncio.Lock()


async def init_db():
    global _client, _db

    # avoid concurrent request to init the db
    async with _lock:
        if _client is None:
            _client = AsyncMongoClient(
                DB_URI,
                tls=True,
                minPoolSize=2,
                maxPoolSize=10,
                maxIdleTimeMS=30000,  # Close idle connections after 30 seconds
                serverSelectionTimeoutMS=10000,  # Timeout for server selection
                connectTimeoutMS=10000,  # Timeout for initial connection
                socketTimeoutMS=10000,  # Timeout for socket operations
                tlsCAFile=certifi.where(),
            )
            _db = _client[MONGO_DB]


async def get_db_conn() -> AsyncDatabase:
    global _client, _db
    if _db is None or _client is None:
        await init_db()
    return _db


async def close_db_conn():
    global _client
    if _client is not None:
        await _client.close()

