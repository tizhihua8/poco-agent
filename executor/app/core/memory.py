import json
from typing import Any

import httpx
from claude_agent_sdk import create_sdk_mcp_server, tool
from claude_agent_sdk.types import McpSdkServerConfig

from app.core.observability.request_context import (
    generate_request_id,
    generate_trace_id,
    get_request_id,
    get_trace_id,
)

MEMORY_MCP_SERVER_KEY = "__poco_memory"


class MemoryClient:
    """Client for manager memory proxy APIs."""

    def __init__(self, base_url: str, session_id: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.session_id = session_id
        self.timeout = timeout

    @staticmethod
    def _trace_headers() -> dict[str, str]:
        return {
            "X-Request-ID": get_request_id() or generate_request_id(),
            "X-Trace-ID": get_trace_id() or generate_trace_id(),
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{path}",
                params=params,
                json=json_body,
                headers=self._trace_headers(),
            )
            response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("Invalid memory proxy response")
        if payload.get("code") != 0:
            raise RuntimeError(str(payload.get("message") or "Memory proxy error"))
        return payload.get("data")

    async def create_memories(
        self,
        *,
        messages: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        body: dict[str, Any] = {
            "session_id": self.session_id,
            "messages": messages,
        }
        if metadata is not None:
            body["metadata"] = metadata
        return await self._request("POST", "/api/v1/memories", json_body=body)

    async def list_memories(self) -> Any:
        return await self._request(
            "GET",
            "/api/v1/memories",
            params={"session_id": self.session_id},
        )

    async def search_memories(
        self,
        *,
        query: str,
        filters: dict[str, Any] | None = None,
    ) -> Any:
        body: dict[str, Any] = {
            "session_id": self.session_id,
            "query": query,
        }
        if filters is not None:
            body["filters"] = filters
        return await self._request("POST", "/api/v1/memories/search", json_body=body)

    async def get_memory(self, memory_id: str) -> Any:
        return await self._request(
            "GET",
            f"/api/v1/memories/{memory_id}",
            params={"session_id": self.session_id},
        )

    async def update_memory(self, *, memory_id: str, data: dict[str, Any]) -> Any:
        return await self._request(
            "PUT",
            f"/api/v1/memories/{memory_id}",
            json_body={"session_id": self.session_id, "data": data},
        )

    async def get_memory_history(self, memory_id: str) -> Any:
        return await self._request(
            "GET",
            f"/api/v1/memories/{memory_id}/history",
            params={"session_id": self.session_id},
        )

    async def delete_memory(self, memory_id: str) -> Any:
        return await self._request(
            "DELETE",
            f"/api/v1/memories/{memory_id}",
            params={"session_id": self.session_id},
        )

    async def delete_all_memories(self) -> Any:
        return await self._request(
            "DELETE",
            "/api/v1/memories",
            params={"session_id": self.session_id},
        )


def _format_tool_result(title: str, data: Any) -> dict[str, Any]:
    body = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    return {"content": [{"type": "text", "text": f"{title}\n{body}"}]}


async def _run_tool(title: str, operation) -> dict[str, Any]:
    try:
        result = await operation
    except Exception as exc:
        return _format_tool_result(f"{title}_error", {"error": str(exc)})
    return _format_tool_result(title, result)


def _extract_messages(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    messages: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if not isinstance(role, str) or not isinstance(content, str):
            continue
        clean_role = role.strip()
        clean_content = content.strip()
        if not clean_role or not clean_content:
            continue
        messages.append({"role": clean_role, "content": clean_content})
    return messages


def create_memory_mcp_server(memory_client: MemoryClient) -> McpSdkServerConfig:
    """Create an in-process SDK MCP server for memory management."""

    @tool(
        "memory_create",
        "Create user-level memories from messages",
        {"messages": list, "metadata": dict | None},
    )
    async def memory_create(args: dict[str, Any]) -> dict[str, Any]:
        messages = _extract_messages(args.get("messages"))
        if not messages:
            return _format_tool_result(
                "memory_create_error",
                {"error": "messages must be a non-empty list of {role, content}"},
            )
        metadata = args.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            return _format_tool_result(
                "memory_create_error",
                {"error": "metadata must be an object when provided"},
            )
        return await _run_tool(
            "memory_create",
            memory_client.create_memories(messages=messages, metadata=metadata),
        )

    @tool(
        "memory_search",
        "Search user-level memories",
        {"query": str, "filters": dict | None},
    )
    async def memory_search(args: dict[str, Any]) -> dict[str, Any]:
        query = args.get("query")
        if not isinstance(query, str) or not query.strip():
            return _format_tool_result(
                "memory_search_error",
                {"error": "query must be a non-empty string"},
            )
        filters = args.get("filters")
        if filters is not None and not isinstance(filters, dict):
            return _format_tool_result(
                "memory_search_error",
                {"error": "filters must be an object when provided"},
            )
        return await _run_tool(
            "memory_search",
            memory_client.search_memories(query=query.strip(), filters=filters),
        )

    @tool(
        "memory_list",
        "List user-level memories",
        {},
    )
    async def memory_list(args: dict[str, Any]) -> dict[str, Any]:
        _ = args
        return await _run_tool("memory_list", memory_client.list_memories())

    @tool(
        "memory_get",
        "Get one memory by id",
        {"memory_id": str},
    )
    async def memory_get(args: dict[str, Any]) -> dict[str, Any]:
        memory_id = args.get("memory_id")
        if not isinstance(memory_id, str) or not memory_id.strip():
            return _format_tool_result(
                "memory_get_error",
                {"error": "memory_id must be a non-empty string"},
            )
        return await _run_tool(
            "memory_get",
            memory_client.get_memory(memory_id.strip()),
        )

    @tool(
        "memory_update",
        "Update one memory by id",
        {"memory_id": str, "data": dict},
    )
    async def memory_update(args: dict[str, Any]) -> dict[str, Any]:
        memory_id = args.get("memory_id")
        data = args.get("data")
        if not isinstance(memory_id, str) or not memory_id.strip():
            return _format_tool_result(
                "memory_update_error",
                {"error": "memory_id must be a non-empty string"},
            )
        if not isinstance(data, dict):
            return _format_tool_result(
                "memory_update_error",
                {"error": "data must be an object"},
            )
        return await _run_tool(
            "memory_update",
            memory_client.update_memory(
                memory_id=memory_id.strip(),
                data=data,
            ),
        )

    @tool(
        "memory_history",
        "Get memory history by id",
        {"memory_id": str},
    )
    async def memory_history(args: dict[str, Any]) -> dict[str, Any]:
        memory_id = args.get("memory_id")
        if not isinstance(memory_id, str) or not memory_id.strip():
            return _format_tool_result(
                "memory_history_error",
                {"error": "memory_id must be a non-empty string"},
            )
        return await _run_tool(
            "memory_history",
            memory_client.get_memory_history(memory_id.strip()),
        )

    @tool(
        "memory_delete",
        "Delete one memory by id",
        {"memory_id": str},
    )
    async def memory_delete(args: dict[str, Any]) -> dict[str, Any]:
        memory_id = args.get("memory_id")
        if not isinstance(memory_id, str) or not memory_id.strip():
            return _format_tool_result(
                "memory_delete_error",
                {"error": "memory_id must be a non-empty string"},
            )
        return await _run_tool(
            "memory_delete",
            memory_client.delete_memory(memory_id.strip()),
        )

    @tool(
        "memory_delete_all",
        "Delete all user-level memories",
        {},
    )
    async def memory_delete_all(args: dict[str, Any]) -> dict[str, Any]:
        _ = args
        return await _run_tool(
            "memory_delete_all",
            memory_client.delete_all_memories(),
        )

    return create_sdk_mcp_server(
        name=MEMORY_MCP_SERVER_KEY,
        version="1.0.0",
        tools=[
            memory_create,
            memory_list,
            memory_search,
            memory_get,
            memory_update,
            memory_history,
            memory_delete,
            memory_delete_all,
        ],
    )
