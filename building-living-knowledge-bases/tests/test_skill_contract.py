import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_skill_declares_complete_lifecycle_and_safety_contract(self) -> None:
        content = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertRegex(content, r"name: building-living-knowledge-bases")
        for operation in ("Initialize", "Activate", "Ingest", "Query", "Maintain", "Measure"):
            self.assertIn(f"## {operation}", content)
        self.assertIn("Raw sources are immutable", content)
        self.assertIn("at most five items", content)
        self.assertIn("Do not write files for an ordinary query", content)
        self.assertIn("KB_SCHEMA.md", content)
        self.assertIn("wiki/index.md", content)
        self.assertIn("wiki/log.md", content)

    def test_skill_declares_complete_seven_blade_and_soft_gate_contract(self) -> None:
        content = (SKILL_ROOT / "SKILL.md").read_text()
        for blade in ("Paradox", "Leverage", "Root cause", "Inversion", "Analogy", "Plain language", "Scale"):
            self.assertIn(blade, content)
        self.assertIn("Four-Gates", content)
        self.assertIn("Pass", content)
        self.assertIn("Not pass", content)
        self.assertRegex(content, r"(?i)does not block|never blocks")
        self.assertNotRegex(content, r"Four-Gate-[1-4]")

    def test_skill_has_no_placeholders(self) -> None:
        content = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIsNone(re.search(r"\b(?:TODO|TBD)\b", content))


if __name__ == "__main__":
    unittest.main()
