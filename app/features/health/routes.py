from fastapi import APIRouter, Request, Depends
from features.health.v1.health import health_check
from middlewares.limiter import limiter
from utils.get_current_user import get_current_admin_user
from utils.core_response import core_response

router = APIRouter()


@router.get("/db")
@limiter.limit("60/minute")
async def get_db_health(request: Request, current_user: dict = Depends(get_current_admin_user)):
    """Get database health status (admin only)"""
    return await health_check()
