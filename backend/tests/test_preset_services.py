from datetime import UTC, datetime
import unittest
import uuid
from unittest.mock import MagicMock, patch

from app.core.errors.error_codes import ErrorCode
from app.core.errors.exceptions import AppException
from app.models.preset import Preset
from app.models.project import Project
from app.models.project_preset import ProjectPreset
from app.schemas.preset import PresetCreateRequest, PresetUpdateRequest
from app.schemas.session import SessionCreateRequest, TaskConfig
from app.services.preset_service import PresetService
from app.services.project_preset_service import ProjectPresetService
from app.services.session_service import SessionService


class PresetServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PresetService()
        self.db = MagicMock()
        self.user_id = "user-1"
        self.now = datetime.now(UTC)

    @patch("app.services.preset_service.PresetRepository.exists_by_user_name")
    def test_create_preset_rejects_duplicate_name(self, exists_by_user_name: MagicMock) -> None:
        exists_by_user_name.return_value = True

        with self.assertRaises(AppException) as context:
            self.service.create_preset(
                self.db,
                self.user_id,
                PresetCreateRequest(name="  Frontend  "),
            )

        self.assertEqual(context.exception.error_code, ErrorCode.PRESET_ALREADY_EXISTS)
        exists_by_user_name.assert_called_once_with(self.db, self.user_id, "Frontend")

    @patch.object(PresetService, "_validate_components")
    @patch("app.services.preset_service.PresetRepository.create")
    @patch("app.services.preset_service.PresetRepository.exists_by_user_name")
    def test_create_preset_persists_trimmed_fields(
        self,
        exists_by_user_name: MagicMock,
        create: MagicMock,
        validate_components: MagicMock,
    ) -> None:
        exists_by_user_name.return_value = False

        created_preset: Preset | None = None

        def capture_create(_db: MagicMock, preset: Preset) -> Preset:
            nonlocal created_preset
            created_preset = preset
            preset.id = 11
            preset.created_at = self.now
            preset.updated_at = self.now
            return preset

        create.side_effect = capture_create
        self.db.refresh.side_effect = lambda _: None

        result = self.service.create_preset(
            self.db,
            self.user_id,
            PresetCreateRequest(
                name="  Frontend Delivery  ",
                description="  Reusable flow  ",
                color="#0ea5e9",
                browser_enabled=True,
                skill_ids=[1, 2],
            ),
        )

        self.assertIsNotNone(created_preset)
        assert created_preset is not None
        self.assertEqual(created_preset.name, "Frontend Delivery")
        self.assertEqual(created_preset.description, "Reusable flow")
        self.assertEqual(created_preset.user_id, self.user_id)
        self.assertTrue(created_preset.browser_enabled)
        self.assertEqual(created_preset.skill_ids, [1, 2])
        validate_components.assert_called_once()
        self.db.commit.assert_called_once()
        self.assertEqual(result.preset_id, 11)
        self.assertEqual(result.name, "Frontend Delivery")
        self.assertEqual(result.description, "Reusable flow")

    @patch.object(PresetService, "_validate_components")
    @patch("app.services.preset_service.PresetRepository.exists_by_user_name")
    @patch("app.services.preset_service.PresetRepository.get_by_id")
    def test_update_preset_rejects_blank_name(
        self,
        get_by_id: MagicMock,
        exists_by_user_name: MagicMock,
        validate_components: MagicMock,
    ) -> None:
        get_by_id.return_value = Preset(
            id=7,
            user_id=self.user_id,
            name="Existing",
            description=None,
            icon="default",
            color=None,
            prompt_template=None,
            browser_enabled=False,
            memory_enabled=False,
            skill_ids=[],
            mcp_server_ids=[],
            plugin_ids=[],
            subagent_configs=[],
            is_deleted=False,
            created_at=self.now,
            updated_at=self.now,
        )
        exists_by_user_name.return_value = False

        with self.assertRaises(AppException) as context:
            self.service.update_preset(
                self.db,
                self.user_id,
                7,
                PresetUpdateRequest(name="   "),
            )

        self.assertEqual(context.exception.error_code, ErrorCode.BAD_REQUEST)
        validate_components.assert_not_called()

    @patch("app.services.preset_service.ProjectPresetRepository.count_projects_using_preset")
    @patch("app.services.preset_service.PresetRepository.get_by_id")
    def test_delete_preset_rejects_project_usage(
        self,
        get_by_id: MagicMock,
        count_projects_using_preset: MagicMock,
    ) -> None:
        get_by_id.return_value = Preset(
            id=9,
            user_id=self.user_id,
            name="Shared",
            description=None,
            icon="default",
            color=None,
            prompt_template=None,
            browser_enabled=False,
            memory_enabled=False,
            skill_ids=[],
            mcp_server_ids=[],
            plugin_ids=[],
            subagent_configs=[],
            is_deleted=False,
            created_at=self.now,
            updated_at=self.now,
        )
        count_projects_using_preset.return_value = 2

        with self.assertRaises(AppException) as context:
            self.service.delete_preset(self.db, self.user_id, 9)

        self.assertEqual(context.exception.error_code, ErrorCode.BAD_REQUEST)
        self.db.commit.assert_not_called()


class ProjectPresetServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ProjectPresetService()
        self.db = MagicMock()
        self.user_id = "user-1"
        self.project_id = uuid.uuid4()
        self.now = datetime.now(UTC)

    @patch("app.services.project_preset_service.ProjectPresetRepository.get_default_preset")
    @patch("app.services.project_preset_service.ProjectPresetRepository.get_max_sort_order")
    @patch("app.services.project_preset_service.ProjectPresetRepository.add_to_project_record")
    @patch("app.services.project_preset_service.ProjectPresetRepository.is_preset_in_project")
    @patch.object(ProjectPresetService, "_get_preset_owned_by_user")
    @patch.object(ProjectPresetService, "_get_project_owned_by_user")
    def test_add_preset_to_project_sets_first_item_as_default(
        self,
        get_project_owned_by_user: MagicMock,
        get_preset_owned_by_user: MagicMock,
        is_preset_in_project: MagicMock,
        add_to_project_record: MagicMock,
        get_max_sort_order: MagicMock,
        get_default_preset: MagicMock,
    ) -> None:
        get_project_owned_by_user.return_value = Project(
            id=self.project_id,
            user_id=self.user_id,
            name="Project",
        )
        get_preset_owned_by_user.return_value = Preset(
            id=3,
            user_id=self.user_id,
            name="Preset",
            description=None,
            icon="default",
            color=None,
            prompt_template=None,
            browser_enabled=False,
            memory_enabled=False,
            skill_ids=[],
            mcp_server_ids=[],
            plugin_ids=[],
            subagent_configs=[],
            is_deleted=False,
            created_at=self.now,
            updated_at=self.now,
        )
        is_preset_in_project.return_value = False
        get_max_sort_order.return_value = 4
        get_default_preset.return_value = None
        added = ProjectPreset(
            id=10,
            project_id=self.project_id,
            preset_id=3,
            is_default=True,
            sort_order=5,
            created_at=self.now,
            updated_at=self.now,
        )
        added.preset = get_preset_owned_by_user.return_value
        add_to_project_record.return_value = added
        self.db.refresh.side_effect = lambda _: None

        result = self.service.add_preset_to_project(
            self.db,
            project_id=self.project_id,
            user_id=self.user_id,
            preset_id=3,
        )

        add_to_project_record.assert_called_once_with(
            self.db,
            project_id=self.project_id,
            preset_id=3,
            is_default=True,
            sort_order=5,
        )
        self.db.commit.assert_called_once()
        self.assertTrue(result.is_default)
        self.assertEqual(result.sort_order, 5)

    @patch("app.services.project_preset_service.ProjectPresetRepository.set_default_preset")
    @patch("app.services.project_preset_service.ProjectPresetRepository.list_by_project")
    @patch("app.services.project_preset_service.ProjectPresetRepository.remove_from_project")
    @patch("app.services.project_preset_service.ProjectPresetRepository.get_by_project_and_preset")
    @patch.object(ProjectPresetService, "_get_project_owned_by_user")
    def test_remove_default_preset_promotes_first_remaining_item(
        self,
        get_project_owned_by_user: MagicMock,
        get_by_project_and_preset: MagicMock,
        remove_from_project: MagicMock,
        list_by_project: MagicMock,
        set_default_preset: MagicMock,
    ) -> None:
        get_project_owned_by_user.return_value = Project(
            id=self.project_id,
            user_id=self.user_id,
            name="Project",
        )
        removed = ProjectPreset(
            id=1,
            project_id=self.project_id,
            preset_id=11,
            is_default=True,
            sort_order=0,
            created_at=self.now,
            updated_at=self.now,
        )
        promoted = ProjectPreset(
            id=2,
            project_id=self.project_id,
            preset_id=12,
            is_default=False,
            sort_order=1,
            created_at=self.now,
            updated_at=self.now,
        )
        get_by_project_and_preset.return_value = removed
        list_by_project.return_value = [promoted]

        self.service.remove_preset_from_project(
            self.db,
            project_id=self.project_id,
            user_id=self.user_id,
            preset_id=11,
        )

        remove_from_project.assert_called_once_with(self.db, removed)
        self.db.flush.assert_called_once()
        set_default_preset.assert_called_once_with(self.db, self.project_id, 12)
        self.db.commit.assert_called_once()


class SessionPresetConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = SessionService()
        self.db = MagicMock()
        self.user_id = "user-1"

    @patch("app.services.session_service.SessionRepository.create")
    def test_create_session_persists_only_explicit_preset_config(
        self,
        create: MagicMock,
    ) -> None:
        session = MagicMock()
        create.return_value = session

        self.service.create_session(
            self.db,
            self.user_id,
            SessionCreateRequest(config=TaskConfig(preset_id=8)),
        )

        create.assert_called_once_with(
            session_db=self.db,
            user_id=self.user_id,
            config={"preset_id": 8},
            project_id=None,
            kind="chat",
        )
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(session)


if __name__ == "__main__":
    unittest.main()
