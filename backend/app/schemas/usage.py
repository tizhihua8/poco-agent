from typing import Any

from pydantic import BaseModel


class UsageResponse(BaseModel):
    """Usage statistics response."""

    total_duration_ms: int | None
    usage_json: dict[str, Any] | None
