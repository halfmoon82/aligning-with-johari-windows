import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "init_kb.py"


class InitKnowledgeBaseTests(unittest.TestCase):
    def run_init(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--json", *extra],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dry_run_reports_without_creating_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "kb"
            result = self.run_init(root, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "dry-run")
            self.assertFalse(root.exists())
            self.assertTrue(any(item["path"] == "KB_SCHEMA.md" for item in payload["actions"]))

    def test_init_creates_minimal_three_layer_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "kb"
            result = self.run_init(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "KB_SCHEMA.md").is_file())
            self.assertTrue((root / "raw" / ".gitkeep").is_file())
            self.assertEqual((root / "wiki" / "index.md").read_text(), "# Knowledge Base Index\n")
            self.assertEqual((root / "wiki" / "log.md").read_text(), "# Knowledge Base Log\n")

    def test_second_init_is_idempotent_and_preserves_existing_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "kb"
            root.mkdir()
            agents = root / "AGENTS.md"
            agents.write_text("# Existing project rules\n")
            first = self.run_init(root)
            self.assertEqual(first.returncode, 0, first.stderr)
            schema = root / "KB_SCHEMA.md"
            schema.write_text("# Customized schema\n")

            second = self.run_init(root)
            self.assertEqual(second.returncode, 0, second.stderr)
            payload = json.loads(second.stdout)
            self.assertEqual(schema.read_text(), "# Customized schema\n")
            self.assertEqual(agents.read_text(), "# Existing project rules\n")
            self.assertTrue(all(item["action"] == "keep" for item in payload["actions"]))

    def test_refuses_broad_root_targets(self) -> None:
        result = self.run_init(Path("/"), "--dry-run")
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "error")

    def test_refuses_symlinked_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            outside = base / "outside"
            outside.mkdir()
            root = base / "kb"
            root.symlink_to(outside, target_is_directory=True)

            result = self.run_init(root)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "error")
            self.assertEqual(list(outside.iterdir()), [])

    def test_refuses_managed_directory_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "kb"
            root.mkdir()
            outside = base / "outside"
            outside.mkdir()
            (root / "raw").symlink_to(outside, target_is_directory=True)

            result = self.run_init(root)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertFalse((outside / ".gitkeep").exists())

    def test_refuses_dangling_managed_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "kb"
            root.mkdir()
            (root / "wiki").symlink_to(base / "missing", target_is_directory=True)

            result = self.run_init(root, "--dry-run")

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "error")

    def test_refuses_non_system_symlink_ancestor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            outside = base / "outside"
            outside.mkdir()
            linked_parent = base / "linked-parent"
            linked_parent.symlink_to(outside, target_is_directory=True)
            root = linked_parent / "kb"

            result = self.run_init(root)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertFalse((outside / "kb").exists())


if __name__ == "__main__":
    unittest.main()
