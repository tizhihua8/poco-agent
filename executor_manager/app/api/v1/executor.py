from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.response import Response, ResponseSchema
from app.schemas.task import (
    ContainerDeleteRequest,
    ContainerStatsResponse,
    TaskCancelRequest,
)
from app.scheduler.task_dispatcher import TaskDispatcher
from app.services.executor_runtime_service import ExecutorRuntimeService

router = APIRouter(prefix="/executor", tags=["executor"])
runtime_service = ExecutorRuntimeService()


@router.post("/cancel", response_model=ResponseSchema[dict])
async def cancel_task(request: TaskCancelRequest) -> JSONResponse:
    """Cancel running task and delete container.

    Args:
        request: Cancel task request

    Returns:
        Success response with session_id and status
    """
    if runtime_service.uses_docker_runtime():
        container_pool = TaskDispatcher.get_container_pool()
        await container_pool.cancel_task(request.session_id)

    return Response.success(
        data={"session_id": request.session_id, "status": "canceled"},
        message="Task canceled successfully",
    )


@router.post("/delete", response_model=ResponseSchema[dict])
async def delete_container(request: ContainerDeleteRequest) -> JSONResponse:
    """Delete persistent container explicitly.

    Args:
        request: Delete container request

    Returns:
        Success response with container_id and status
    """
    if runtime_service.uses_docker_runtime():
        container_pool = TaskDispatcher.get_container_pool()
        await container_pool.delete_container(request.container_id)

    return Response.success(
        data={"container_id": request.container_id, "status": "deleted"},
        message="Container deleted successfully",
    )


@router.get("/load", response_model=ResponseSchema[ContainerStatsResponse])
async def get_executor_load() -> JSONResponse:
    """Get executor container load statistics.

    Returns:
        Container statistics response
    """
    if runtime_service.uses_docker_runtime():
        container_pool = TaskDispatcher.get_container_pool()
        stats = container_pool.get_container_stats()
    else:
        stats = runtime_service.get_direct_runtime_stats()

    return Response.success(data=stats)
