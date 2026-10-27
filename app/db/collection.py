from enum import Enum
from pymongo.asynchronous.database import (
    AsyncDatabase,
    AsyncCollection
)


class DBCollection(Enum):
    USERS = "users"
    AUTH_SESSIONS = "auth_sessions"
    NOTIFICATIONS = "notifications"


    def __call__(self, db_conn: AsyncDatabase) -> AsyncCollection:
        return db_conn[self.value]
