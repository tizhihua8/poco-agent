import uuid
from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.errors.error_codes import ErrorCode
from app.core.errors.exceptions import AppException
from app.core.settings import get_settings
from app.repositories.session_repository import SessionRepository

DEFAULT_USER_ID = "default"


def get_current_user_id(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> str:
    """FastAPI dependency for the current user id.

    NOTE: Auth is not implemented yet. For now we allow callers to pass X-User-Id
    and fall back to DEFAULT_USER_ID when absent.
    """
    value = (x_user_id or "").strip()
    return value or DEFAULT_USER_ID


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_internal_token(
    x_internal_token: str | None = Header(default=None, alias="X-Internal-Token"),
) -> None:
    """Validate X-Internal-Token header for internal API endpoints."""
    settings = get_settings()
    if not settings.internal_api_token:
        raise AppException(
            error_code=ErrorCode.FORBIDDEN,
            message="Internal API token is not configured",
        )
    if not x_internal_token or x_internal_token != settings.internal_api_token:
        raise AppException(
            error_code=ErrorCode.FORBIDDEN,
            message="Invalid internal token",
        )


def get_user_id_by_session_id(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> str:
    """Resolve user id by session id for internal APIs."""
    db_session = SessionRepository.get_by_id(db, session_id)
    if not db_session:
        raise AppException(
            error_code=ErrorCode.NOT_FOUND,
            message=f"Session not found: {session_id}",
        )
    return db_session.user_id
