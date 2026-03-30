import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user_id, get_db
from app.schemas.preset import (
    PresetOrderUpdateRequest,
    ProjectPresetAddRequest,
    ProjectPresetResponse,
)
from app.schemas.response import Response, ResponseSchema
from app.services.project_preset_service import ProjectPresetService

router = APIRouter(prefix="/projects/{project_id}/presets", tags=["project-presets"])

service = ProjectPresetService()


@router.get("", response_model=ResponseSchema[list[ProjectPresetResponse]])
async def list_project_presets(
    project_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> JSONResponse:
    result = service.list_project_presets(db, project_id=project_id, user_id=user_id)
    return Response.success(
        data=result,
        message="Project presets retrieved successfully",
    )


@router.post("", response_model=ResponseSchema[ProjectPresetResponse])
async def add_project_preset(
    project_id: uuid.UUID,
    request: ProjectPresetAddRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> JSONResponse:
    result = service.add_preset_to_project(
        db,
        project_id=project_id,
        user_id=user_id,
        preset_id=request.preset_id,
    )
    return Response.success(
        data=result,
        message="Preset added to project successfully",
    )


@router.put(
    "/{preset_id}/default",
    response_model=ResponseSchema[ProjectPresetResponse],
)
async def set_default_project_preset(
    project_id: uuid.UUID,
    preset_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> JSONResponse:
    result = service.set_default_preset(
        db,
        project_id=project_id,
        user_id=user_id,
        preset_id=preset_id,
    )
    return Response.success(
        data=result,
        message="Project default preset updated successfully",
    )


@router.delete("/{preset_id}", response_model=ResponseSchema[dict])
async def remove_project_preset(
    project_id: uuid.UUID,
    preset_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> JSONResponse:
    service.remove_preset_from_project(
        db,
        project_id=project_id,
        user_id=user_id,
        preset_id=preset_id,
    )
    return Response.success(
        data={"project_id": project_id, "preset_id": preset_id},
        message="Preset removed from project successfully",
    )


@router.patch("/{preset_id}/order", response_model=ResponseSchema[ProjectPresetResponse])
async def update_project_preset_order(
    project_id: uuid.UUID,
    preset_id: int,
    request: PresetOrderUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> JSONResponse:
    result = service.update_preset_order(
        db,
        project_id=project_id,
        user_id=user_id,
        preset_id=preset_id,
        sort_order=request.sort_order,
    )
    return Response.success(
        data=result,
        message="Project preset order updated successfully",
    )
