from fastapi import FastAPI, Request
from db.db import init_db, close_db_conn
from contextlib import asynccontextmanager

from middlewares.cors import add_cors_middleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from middlewares.limiter import add_slowapi_middleware, limiter
from features.auth.oauth_service import oauth, init_oauth

from routers.routers import api_router
from config import ENABLE_DOCS


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Initialize OAuth
    init_oauth(app)

    yield

    # Shutdown
    await close_db_conn()


app = FastAPI(
    title="MFA Login",
    swagger_ui_parameters={
        "persistAuthorization": 1,
        "defaultModelsExpandDepth": -1,  # Hides the Schemas section
        "displayRequestDuration": True    # Shows response time in /docs
    },
    lifespan=lifespan,
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_DOCS else None
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

add_cors_middleware(app)
add_slowapi_middleware(app)


app.include_router(api_router, prefix="/api/v1")


@app.get("/")
@limiter.limit("30/minute")
async def root(request: Request):
    return {
        "message": "Welcome to MFA Login API"
    }


@app.get("/app-health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    return {
        "status": "ok",
        "message": "MFA Login is running",
    }
