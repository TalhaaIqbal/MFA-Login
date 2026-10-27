# Logging Guide with App ID

## Adding App ID to Logs

Since logs are handled by the `logging_config` module and likely written by external scraper modules, here's how to include `app_id` in your log entries:

### Method 1: Include app_id in the log message

```python
from logging_config import logger

# When logging from your scraper, include the app_id in the message
app_id = "507f1f77bcf86cd799439011"  # The ObjectId of the app

logger.info(f"Scraper started for app_id: {app_id}")
logger.error(f"Scraping failed for app_id: {app_id}, error: connection timeout")
logger.warning(f"Rate limit reached for app_id: {app_id}")
```

### Method 2: Use a custom LogRecord with app_id

You can create a custom adapter to add app_id to all log records:

```python
import logging
from logging_config import logger

class AppIdAdapter(logging.LoggerAdapter):
    def __init__(self, logger, app_id):
        super().__init__(logger, {})
        self.app_id = app_id

    def process(self, msg, kwargs):
        return f"[app_id: {self.app_id}] {msg}", kwargs

# Usage in your scraper
app_id = "507f1f77bcf86cd799439011"
app_logger = AppIdAdapter(logger, app_id)

app_logger.info("Scraper started")
app_logger.error("Scraping failed")
# This will output: [app_id: 507f1f77bcf86cd799439011] Scraper started
```

### Method 3: Add app_id as an extra field

```python
from logging_config import logger

app_id = "507f1f77bcf86cd799439011"

logger.info("Scraper started", extra={"app_id": app_id})
logger.error("Scraping failed", extra={"app_id": app_id})
```

**Note:** This requires updating the log format in `logging_config.py` to include the extra field:
```python
LOG_FORMAT = "%(levelname)s - %(funcName)s - %(app_id)s - %(message)s"
```

### Method 4: Create a context-aware logger

For more complex scenarios, you can use a context manager:

```python
from contextlib import contextmanager
import logging
from logging_config import logger

@contextmanager
def app_context(app_id):
    """Context manager to add app_id to logs within a block"""
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.app_id = app_id
        return record

    logging.setLogRecordFactory(record_factory)
    try:
        yield
    finally:
        logging.setLogRecordFactory(old_factory)

# Usage
app_id = "507f1f77bcf86cd799439011"

with app_context(app_id):
    logger.info("Scraper started")  # Will include app_id
    logger.error("Scraping failed")  # Will include app_id
```

## Database Schema Update

When storing logs in the database, ensure your log document includes the `app_id` field:

```python
log_document = {
    "app_id": ObjectId(app_id),  # Reference to the app
    "level": "ERROR",
    "message": "Scraping failed",
    "timestamp": datetime.utcnow(),
    "details": {...}
}
```

## Filtering Logs by App ID

When querying logs, you can filter by app_id:

```python
# In your log retrieval function
query = {}
if app_id:
    query["app_id"] = ObjectId(app_id)

logs = await logs_collection.find(query).to_list(length=None)
```

## Recommendation

**Method 1** (including app_id in the message) is the simplest and most compatible with your current `logging_config.py` setup. It doesn't require any changes to the logging configuration and works immediately.

Example:
```python
logger.info(f"Scraper started for app_id: {app_id}")
```
