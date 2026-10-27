from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SessionOut(BaseModel):
    """A single active session belonging to the current user."""

    device: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_seen_at: datetime
    is_current: bool

    model_config = {"from_attributes": True}
