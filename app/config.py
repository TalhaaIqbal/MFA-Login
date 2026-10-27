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

# Validate ENCRYPTION_KEY is a valid Fernet key (44 bytes base64)
if ENCRYPTION_KEY and len(ENCRYPTION_KEY) != 44:
    raise ValueError("ENCRYPTION_KEY must be a 44-byte base64-encoded string (Fernet key)")

# API Documentation - disable in production by default
ENABLE_DOCS: bool = environ.get("ENABLE_DOCS", "false").lower() == "true"

# CORS Configuration
CORS_ORIGINS: list[str] = environ.get("CORS_ORIGINS", "").split(",") if environ.get("CORS_ORIGINS") else []

# Cookie Configuration
# For cross-origin requests, use SameSite=None with Secure=true
# For same-origin, use SameSite=lax
COOKIE_SECURE: bool = environ.get("COOKIE_SECURE", "true").lower() == "true"
COOKIE_SAMESITE: str = environ.get("COOKIE_SAMESITE", "none")  # Changed to 'none' for cross-origin
COOKIE_DOMAIN: str = environ.get("COOKIE_DOMAIN", "")  # Optional: set cookie domain (e.g., .example.com for subdomain sharing)
# Note: partitioned=True requires Python 3.14+ (not supported on Vercel yet)
# Cookie warnings will appear in console but functionality works