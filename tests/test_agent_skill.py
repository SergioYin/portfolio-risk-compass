from pathlib import Path
import unittest


class AgentSkillTests(unittest.TestCase):
    def test_public_agent_skill_exists_with_required_sections(self):
        root = Path(__file__).resolve().parents[1]
        skill_path = root / "skills/agent/portfolio-risk-compass/SKILL.md"

        self.assertTrue(skill_path.is_file())

        text = skill_path.read_text(encoding="utf-8")
        for section in [
            "## Triggers",
            "## Task Routing",
            "## Core Commands",
            "## Inputs",
            "## Outputs",
            "## Validation",
            "## Safety Boundaries",
            "## Response Rules",
            "## Done Criteria",
        ]:
            self.assertIn(section, text)
        self.assertIn("[README](../../../README.md)", text)


if __name__ == "__main__":
    unittest.main()
