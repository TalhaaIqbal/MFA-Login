from fastapi import APIRouter
from features.users.routes import router as user_routes
from features.auth.routes import router as auth_routes
from features.health.routes import router as health_routes

api_router = APIRouter()

api_router.include_router(user_routes, prefix="/users", tags=["Users"])
api_router.include_router(auth_routes, prefix="/auth", tags=["Authentication"])
api_router.include_router(health_routes, prefix="/health", tags=["Health"])
