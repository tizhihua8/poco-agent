from pathlib import Path
import unittest

from app.lifecycle.builtin_skills import BUILTIN_SKILLS


class BuiltinSkillsTests(unittest.TestCase):
    def test_all_skill_assets_are_declared_as_builtin_skills(self) -> None:
        assets_root = Path(__file__).resolve().parents[1] / "assets" / "skills"
        expected_names = sorted(
            path.parent.name for path in assets_root.glob("*/SKILL.md")
        )

        declared_names = sorted(definition.asset_dir_name for definition in BUILTIN_SKILLS)

        self.assertEqual(declared_names, expected_names)


if __name__ == "__main__":
    unittest.main()
