from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateRequest(BaseModel):
    name: str
    description: str | None = None
    repo_url: str | None = None
    git_branch: str | None = None
    git_token_env_key: str | None = None


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    repo_url: str | None = None
    git_branch: str | None = None
    git_token_env_key: str | None = None


class ProjectResponse(BaseModel):
    project_id: UUID = Field(validation_alias="id")
    user_id: str
    name: str
    description: str | None = None
    repo_url: str | None = None
    git_branch: str | None = None
    git_token_env_key: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
