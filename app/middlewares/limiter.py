from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

# Create shared limiter instance
limiter = Limiter(key_func=get_remote_address)

def add_slowapi_middleware(app: FastAPI):
    app.add_middleware(SlowAPIMiddleware)
