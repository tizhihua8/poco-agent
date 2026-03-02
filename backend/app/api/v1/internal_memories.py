from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.deps import get_user_id_by_session_id, require_internal_token
from app.schemas.memory import (
    InternalMemoryCreateRequest,
    InternalMemorySearchRequest,
    InternalMemoryUpdateRequest,
    MemoryCreateRequest,
    MemorySearchRequest,
)
from app.schemas.response import Response, ResponseSchema
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/internal", tags=["internal"])

memory_service = MemoryService()


@router.post("/memories", response_model=ResponseSchema[Any])
async def create_memories_internal(
    request: InternalMemoryCreateRequest,
    _: None = Depends(require_internal_token),
    user_id: str = Depends(get_user_id_by_session_id),
) -> JSONResponse:
    memory_request = MemoryCreateRequest(
        messages=request.messages,
        metadata=request.metadata,
    )
    result = memory_service.create_memories(user_id=user_id, request=memory_request)
    return Response.success(data=result, message="Memory stored successfully")


@router.get("/memories", response_model=ResponseSchema[Any])
async def list_memories_internal(
    _: None = Depends(require_internal_token),
    user_id: str = Depends(get_user_id_by_session_id),
) -> JSONResponse:
    result = memory_service.list_memories(
        user_id=user_id,
    )
    return Response.success(data=result, message="Memories retrieved successfully")


@router.post("/memories/search", response_model=ResponseSchema[Any])
async def search_memories_internal(
    request: InternalMemorySearchRequest,
    _: None = Depends(require_internal_token),
    user_id: str = Depends(get_user_id_by_session_id),
) -> JSONResponse:
    search_request = MemorySearchRequest(
        query=request.query,
        filters=request.filters,
    )
    result = memory_service.search_memories(user_id=user_id, request=search_request)
    return Response.success(data=result, message="Memories searched successfully")


@router.get("/memories/{memory_id}", response_model=ResponseSchema[Any])
async def get_memory_internal(
    memory_id: str,
    _token: None = Depends(require_internal_token),
    _user_id: str = Depends(get_user_id_by_session_id),
) -> JSONResponse:
    result = memory_service.get_memory(memory_id)
    return Response.success(data=result, message="Memory retrieved successfully")


@router.put("/memories/{memory_id}", response_model=ResponseSchema[Any])
async def update_memory_internal(
    memory_id: str,
    request: InternalMemoryUpdateRequest,
    _token: None = Depends(require_internal_token),
    _user_id: str = Depends(get_user_id_by_session_id),
) -> JSONResponse:
    result = memory_service.update_memory(memory_id=memory_id, data=request.data)
    return Response.success(data=result, message="Memory updated successfully")


@router.get("/memories/{memory_id}/history", response_model=ResponseSchema[Any])
async def get_memory_history_internal(
    memory_id: str,
    _token: None = Depends(require_internal_token),
    _user_id: str = Depends(get_user_id_by_session_id),
) -> JSONResponse:
    result = memory_service.get_memory_history(memory_id=memory_id)
    return Response.success(
        data=result, message="Memory history retrieved successfully"
    )


@router.delete("/memories/{memory_id}", response_model=ResponseSchema[dict[str, str]])
async def delete_memory_internal(
    memory_id: str,
    _token: None = Depends(require_internal_token),
    _user_id: str = Depends(get_user_id_by_session_id),
) -> JSONResponse:
    memory_service.delete_memory(memory_id=memory_id)
    return Response.success(
        data={"id": memory_id}, message="Memory deleted successfully"
    )


@router.delete("/memories", response_model=ResponseSchema[dict[str, bool]])
async def delete_all_memories_internal(
    _: None = Depends(require_internal_token),
    user_id: str = Depends(get_user_id_by_session_id),
) -> JSONResponse:
    memory_service.delete_all_memories(
        user_id=user_id,
    )
    return Response.success(
        data={"deleted": True},
        message="All relevant memories deleted successfully",
    )
