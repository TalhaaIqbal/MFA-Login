from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
