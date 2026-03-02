from typing import Any

from pydantic import BaseModel, Field


class MemoryMessage(BaseModel):
    """Memory message payload."""

    role: str = Field(..., description="Role of the message.")
    content: str = Field(..., description="Message content.")


class MemoryConfigureRequest(BaseModel):
    """Request to configure memory backend."""

    enabled: bool | None = Field(
        default=None,
        description="Whether memory is enabled.",
    )
    config: dict[str, Any] | None = Field(
        default=None,
        description="Mem0 configuration payload.",
    )


class MemoryCreateRequest(BaseModel):
    """Request to create memories."""

    messages: list[MemoryMessage] = Field(
        ...,
        min_length=1,
        description="Conversation messages used to extract and store memories.",
    )
    run_id: str | None = None
    metadata: dict[str, Any] | None = None


class MemorySearchRequest(BaseModel):
    """Request to search memories."""

    query: str = Field(..., description="Search query.")
    run_id: str | None = None
    filters: dict[str, Any] | None = None


class MemoryUpdateRequest(BaseModel):
    """Request to update a memory."""

    data: dict[str, Any] = Field(..., description="Updated memory content.")


class InternalMemoryCreateRequest(BaseModel):
    """Internal request to create memories by session scope."""

    messages: list[MemoryMessage] = Field(
        ...,
        min_length=1,
        description="Conversation messages used to extract and store memories.",
    )
    metadata: dict[str, Any] | None = None


class InternalMemorySearchRequest(BaseModel):
    """Internal request to search memories by session scope."""

    query: str = Field(..., description="Search query.")
    filters: dict[str, Any] | None = None


class InternalMemoryUpdateRequest(BaseModel):
    """Internal request to update memory by session scope."""

    data: dict[str, Any] = Field(..., description="Updated memory content.")
