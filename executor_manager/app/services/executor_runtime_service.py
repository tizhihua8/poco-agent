import logging

from app.core.settings import Settings, get_settings
from app.services.workspace_manager import WorkspaceManager

logger = logging.getLogger(__name__)


class ExecutorRuntimeService:
    """Resolve executor and callback endpoints for the active runtime mode."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.workspace_manager = WorkspaceManager()

    def uses_docker_runtime(self) -> bool:
        return self.settings.executor_runtime_mode == "docker"

    def get_executor_url(self) -> str:
        executor_url = (self.settings.executor_url or "").strip().rstrip("/")
        if not executor_url:
            raise ValueError("EXECUTOR_URL is required when EXECUTOR_RUNTIME_MODE=direct")
        return executor_url

    def get_callback_base_url(self) -> str:
        if self.uses_docker_runtime():
            callback_base_url = (self.settings.callback_base_url or "").strip()
        else:
            callback_base_url = (
                self.settings.executor_direct_callback_base_url
                or self.settings.callback_base_url
            )

        normalized = str(callback_base_url or "").strip().rstrip("/")
        if not normalized:
            raise ValueError("Callback base URL cannot be empty")

        if not self.uses_docker_runtime() and "host.docker.internal" in normalized:
            logger.warning(
                "direct_runtime_host_docker_internal_callback_detected",
                extra={"callback_base_url": normalized},
            )
            return normalized.replace("host.docker.internal", "localhost", 1)

        return normalized

    def get_callback_url(self) -> str:
        return f"{self.get_callback_base_url()}/api/v1/callback"

    def resolve_direct_target(
        self,
        *,
        session_id: str,
        user_id: str,
        container_mode: str = "ephemeral",
        container_id: str | None = None,
        browser_enabled: bool = False,
    ) -> tuple[str, str | None]:
        if container_id or container_mode == "persistent":
            logger.warning(
                "direct_runtime_container_settings_ignored",
                extra={
                    "session_id": session_id,
                    "user_id": user_id,
                    "container_mode": container_mode,
                    "container_id": container_id,
                    "browser_enabled": browser_enabled,
                },
            )

        return self.get_executor_url(), None

    def build_runtime_env(
        self,
        *,
        session_id: str,
        user_id: str,
        browser_enabled: bool = False,
    ) -> dict[str, str]:
        workspace_path = str(
            self.workspace_manager.get_workspace_volume(
                user_id=user_id,
                session_id=session_id,
            )
        )

        env = {
            "WORKSPACE_PATH": workspace_path,
            "ANTHROPIC_BASE_URL": self.settings.anthropic_base_url,
            "DEFAULT_MODEL": self.settings.default_model,
            "EXECUTOR_TIMEZONE": self.settings.executor_timezone,
        }

        anthropic_api_key = (self.settings.anthropic_api_key or "").strip()
        if anthropic_api_key:
            env["ANTHROPIC_API_KEY"] = anthropic_api_key

        if browser_enabled:
            env["POCO_BROWSER_VIEWPORT_SIZE"] = self.settings.poco_browser_viewport_size
            env["PLAYWRIGHT_MCP_OUTPUT_MODE"] = self.settings.playwright_mcp_output_mode
            env["PLAYWRIGHT_MCP_IMAGE_RESPONSES"] = (
                self.settings.playwright_mcp_image_responses
            )

        return env

    def get_direct_runtime_stats(self) -> dict[str, int | list[dict] | str | None]:
        return {
            "runtime_mode": "direct",
            "executor_url": self.get_executor_url(),
            "total_active": 0,
            "persistent_containers": 0,
            "ephemeral_containers": 0,
            "containers": [],
        }
