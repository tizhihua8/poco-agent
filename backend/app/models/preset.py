from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    ARRAY,
    Boolean,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project


class Preset(Base, TimestampMixin):
    __tablename__ = "presets"
    __table_args__ = (
        UniqueConstraint("user_id", "name", "is_deleted", name="uq_preset_user_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    visual_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="preset-visual-01",
        server_default=text("'preset-visual-01'"),
    )

    prompt_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    browser_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    memory_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    skill_ids: Mapped[list[int]] = mapped_column(
        ARRAY(Integer),
        nullable=False,
        default=list,
        server_default=text("'{}'"),
    )
    mcp_server_ids: Mapped[list[int]] = mapped_column(
        ARRAY(Integer),
        nullable=False,
        default=list,
        server_default=text("'{}'"),
    )
    plugin_ids: Mapped[list[int]] = mapped_column(
        ARRAY(Integer),
        nullable=False,
        default=list,
        server_default=text("'{}'"),
    )
    subagent_configs: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'::json"),
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    default_projects: Mapped[list["Project"]] = relationship(
        back_populates="default_preset",
        foreign_keys="Project.default_preset_id",
    )
