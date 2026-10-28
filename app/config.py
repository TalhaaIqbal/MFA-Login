from os import environ
from dotenv import load_dotenv
from urllib.parse import quote_plus


load_dotenv()

APP_NAME: str = environ.get("APP_NAME", "Scraper Dashboard")

MONGO_USER = quote_plus(environ["DB_USER"])
MONGO_PASS = quote_plus(environ["DB_PASSWORD"])
MONGO_HOST = environ["DB_HOST"]
MONGO_DB   = environ["DB_NAME"]

DB_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}/{MONGO_DB}"
SLACK_WEBHOOK_URL: str = environ.get("SLACK_WEBHOOK_URL")

ADMIN_EMAIL: str = environ.get("ADMIN_EMAIL", "")
ADMIN_PASSWORD: str = environ.get("ADMIN_PASSWORD", "")

# Encryption Configuration
ENCRYPTION_KEY: str = environ.get("ENCRYPTION_KEY", "")

# OAuth Configuration
GOOGLE_CLIENT_ID: str = environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI: str = environ.get("GOOGLE_AUTHORIZED_REDIRECT_URI", "")

GITHUB_CLIENT_ID: str = environ.get("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET: str = environ.get("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI: str = environ.get("GITHUB_AUTHORIZED_REDIRECT_URI", "")

MICROSOFT_CLIENT_ID: str = environ.get("MICROSOFT_CLIENT_ID", "")
MICROSOFT_CLIENT_SECRET: str = environ.get("MICROSOFT_CLIENT_SECRET") or environ.get("MICORSOFT_CLIENT_SECRET", "")
MICROSOFT_TENANT_ID: str = environ.get("MICROSOFT_TENANT_ID", "common")
MICROSOFT_REDIRECT_URI: str = environ.get("MICROSOFT_AUTHORIZED_REDIRECT_URI", "")

# Email Configuration
SMTP_HOST: str = environ.get("SMTP_HOST", "")
SMTP_PORT: int = int(environ.get("SMTP_PORT", "587"))
SMTP_USER: str = environ.get("SMTP_USER", "")
SMTP_PASSWORD: str = environ.get("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL: str = environ.get("SMTP_FROM_EMAIL", "")
SMTP_FROM_NAME: str = environ.get("SMTP_FROM_NAME", "MFA Login")

# Validate ENCRYPTION_KEY is a valid Fernet key (44 bytes base64)
if ENCRYPTION_KEY and len(ENCRYPTION_KEY) != 44:
    raise ValueError("ENCRYPTION_KEY must be a 44-byte base64-encoded string (Fernet key)")

# API Documentation - disable in production by default
ENABLE_DOCS: bool = environ.get("ENABLE_DOCS", "false").lower() == "true"

# CORS Configuration
CORS_ORIGINS: list[str] = environ.get("CORS_ORIGINS", "").split(",") if environ.get("CORS_ORIGINS") else []

# Environment Configuration
ENVIRONMENT: str = environ.get("ENVIRONMENT", "local").lower()  # 'local' or 'production'

# Frontend URL for OAuth redirects
FRONTEND_URL: str = environ.get("FRONTEND_URL", "http://localhost:5173")

# Cookies: lax locally (same-site localhost), none+secure in production
SESSION_SECRET: str = environ.get("SESSION_SECRET") or ENCRYPTION_KEY or "dev-only-change-me"
COOKIE_SECURE: bool = ENVIRONMENT == "production"
COOKIE_SAMESITE: str = environ.get("COOKIE_SAMESITE", "none" if COOKIE_SECURE else "lax")
COOKIE_DOMAIN: str = environ.get("COOKIE_DOMAIN", "")
COOKIE_PARTITIONED: bool = ENVIRONMENT == "production"

# Session max age in seconds (default: 2 hours), also used for cookie max age
MAX_AGE: int = int(environ.get("MAX_AGE", "7200"))  # 2 hours in seconds (default)
