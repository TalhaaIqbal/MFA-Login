
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS


def add_cors_middleware(app: FastAPI):
    # Use environment variable for origins, with fallback to common development origins
    origins = CORS_ORIGINS if CORS_ORIGINS else [
        'http://localhost:5173',
        'http://localhost:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000'
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # allow_headers=["Content-Type", "Authorization", "X-2FA-Token"],
        expose_headers=["Content-Type", "Authorization"],
        max_age=600,
    )
