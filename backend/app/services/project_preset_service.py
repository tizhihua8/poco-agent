from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors.error_codes import ErrorCode
from app.core.errors.exceptions import AppException
from app.repositories.preset_repository import PresetRepository
from app.repositories.project_preset_repository import ProjectPresetRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.preset import ProjectPresetResponse


class ProjectPresetService:
    def list_project_presets(
        self,
        db: Session,
        *,
        project_id: UUID,
        user_id: str,
    ) -> list[ProjectPresetResponse]:
        self._get_project_owned_by_user(db, project_id=project_id, user_id=user_id)
        items = ProjectPresetRepository.list_by_project(db, project_id)
        return [ProjectPresetResponse.model_validate(item) for item in items]

    def add_preset_to_project(
        self,
        db: Session,
        *,
        project_id: UUID,
        user_id: str,
        preset_id: int,
    ) -> ProjectPresetResponse:
        self._get_project_owned_by_user(db, project_id=project_id, user_id=user_id)
        self._get_preset_owned_by_user(db, preset_id=preset_id, user_id=user_id)

        if ProjectPresetRepository.is_preset_in_project(db, project_id, preset_id):
            raise AppException(
                error_code=ErrorCode.BAD_REQUEST,
                message="Preset is already added to the project",
            )

        max_sort_order = ProjectPresetRepository.get_max_sort_order(db, project_id)
        item = ProjectPresetRepository.add_to_project_record(
            db,
            project_id=project_id,
            preset_id=preset_id,
            is_default=ProjectPresetRepository.get_default_preset(db, project_id)
            is None,
            sort_order=max_sort_order + 1,
        )
        db.commit()
        db.refresh(item)
        return ProjectPresetResponse.model_validate(item)

    def set_default_preset(
        self,
        db: Session,
        *,
        project_id: UUID,
        user_id: str,
        preset_id: int,
    ) -> ProjectPresetResponse:
        self._get_project_owned_by_user(db, project_id=project_id, user_id=user_id)
        self._get_preset_owned_by_user(db, preset_id=preset_id, user_id=user_id)

        item = ProjectPresetRepository.set_default_preset(db, project_id, preset_id)
        if item is None:
            raise AppException(
                error_code=ErrorCode.BAD_REQUEST,
                message="Preset is not assigned to the project",
            )

        db.commit()
        db.refresh(item)
        return ProjectPresetResponse.model_validate(item)

    def remove_preset_from_project(
        self,
        db: Session,
        *,
        project_id: UUID,
        user_id: str,
        preset_id: int,
    ) -> None:
        self._get_project_owned_by_user(db, project_id=project_id, user_id=user_id)
        item = ProjectPresetRepository.get_by_project_and_preset(db, project_id, preset_id)
        if item is None:
            raise AppException(
                error_code=ErrorCode.BAD_REQUEST,
                message="Preset is not assigned to the project",
            )

        removed_default = item.is_default
        ProjectPresetRepository.remove_from_project(db, item)
        db.flush()

        if removed_default:
            remaining = ProjectPresetRepository.list_by_project(db, project_id)
            if remaining:
                ProjectPresetRepository.set_default_preset(
                    db,
                    project_id,
                    remaining[0].preset_id,
                )

        db.commit()

    def update_preset_order(
        self,
        db: Session,
        *,
        project_id: UUID,
        user_id: str,
        preset_id: int,
        sort_order: int,
    ) -> ProjectPresetResponse:
        self._get_project_owned_by_user(db, project_id=project_id, user_id=user_id)
        item = ProjectPresetRepository.get_by_project_and_preset(db, project_id, preset_id)
        if item is None:
            raise AppException(
                error_code=ErrorCode.BAD_REQUEST,
                message="Preset is not assigned to the project",
            )

        ProjectPresetRepository.update_sort_order(db, item, sort_order)
        db.commit()
        db.refresh(item)
        return ProjectPresetResponse.model_validate(item)

    @staticmethod
    def _get_project_owned_by_user(
        db: Session,
        *,
        project_id: UUID,
        user_id: str,
    ):
        project = ProjectRepository.get_by_id(db, project_id)
        if not project or project.user_id != user_id:
            raise AppException(
                error_code=ErrorCode.PROJECT_NOT_FOUND,
                message=f"Project not found: {project_id}",
            )
        return project

    @staticmethod
    def _get_preset_owned_by_user(
        db: Session,
        *,
        preset_id: int,
        user_id: str,
    ):
        preset = PresetRepository.get_by_id(db, preset_id, user_id)
        if not preset:
            raise AppException(
                error_code=ErrorCode.PRESET_NOT_FOUND,
                message=f"Preset not found: {preset_id}",
            )
        return preset
