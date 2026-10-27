import sys
import logging
import os
import requests


# Define log format
LOG_FORMAT = "%(levelname)s - %(funcName)s - %(message)s"

app_name = os.getenv("APP_NAME", "Scraper Dashboard")


def redact_email(email: str) -> str:
    """Redact email for logging purposes while preserving format"""
    if not email or '@' not in email:
        return '[REDACTED]'
    local, domain = email.split('@', 1)
    if len(local) > 2:
        redacted_local = local[0] + '*' * (len(local) - 2) + local[-1]
    else:
        redacted_local = '*' * len(local)
    return f"{redacted_local}@{domain}"



#Configure Slack Handler Class
class SlackHandler(logging.Handler):
    def __init__(self, webhook_url: str, level: logging.WARNING):
        super().__init__(level)
        self.webhook_url = webhook_url

    def emit(self, record: logging.LogRecord):
        try:
            message = self.format(record)
            # Limit message length to avoid large payloads
            if len(message) > 1000:
                message = message[:1000] + '... [truncated]'
            payload = {"text": f"*[{record.levelname}]* `{record.name}`\n`{record.pathname}`\n```{message}```"}
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception:
            self.handleError(record)


handlers = [
    logging.StreamHandler(sys.stdout)
]

slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

if slack_webhook_url:
    handlers.append(
        SlackHandler(slack_webhook_url, logging.WARNING)
    )

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=handlers
)

# Get logger
logger = logging.getLogger(app_name)

