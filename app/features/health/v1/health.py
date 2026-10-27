from time import time
from db.db import get_db_conn
from utils.core_response import core_response
from logging_config import logger
from datetime import datetime, timedelta

# Simple in-memory cache
_health_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 30  # 30 seconds TTL
}


async def health_check():
    """Check database health with caching"""
    current_time = time()

    # Check if cache is valid
    if (_health_cache["data"] is not None and
        current_time - _health_cache["timestamp"] < _health_cache["ttl"]):
        return _health_cache["data"]

    # Perform health check
    try:
        start_time = time()
        db = await get_db_conn()
        await db.client.admin.command("ping")
        end_time = time()

        latency_ms = (end_time - start_time) * 1000

        response = await core_response(
            status_code=200,
            message="Database is healthy",
            data={
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "last_check": datetime.utcnow().isoformat(),
                "database": "mongodb"
            }
        )

        # Update cache
        _health_cache["data"] = response
        _health_cache["timestamp"] = current_time

        return response

    except Exception as e:
        logger.error(f"Database health check failed: {e}")

        response = await core_response(
            status_code=503,
            message="Database connection failed",
            data={
                "status": "unhealthy",
                "latency_ms": None,
                "last_check": datetime.utcnow().isoformat(),
                "database": "mongodb"
            }
        )

        # Cache error response for shorter time (5 seconds)
        _health_cache["data"] = response
        _health_cache["timestamp"] = current_time
        _health_cache["ttl"] = 5

        return response
