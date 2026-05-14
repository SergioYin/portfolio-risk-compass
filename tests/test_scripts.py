from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ScriptTests(unittest.TestCase):
    def test_sync_local_skill_adapts_readme_link(self):
        sync_local_skill = load_script("sync_local_skill")
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "skills"
            with redirect_stdout(io.StringIO()):
                result = sync_local_skill.main(["--target-dir", str(target_dir)])

            self.assertEqual(result, 0)
            skill_path = target_dir / "portfolio-risk-compass/SKILL.md"
            text = skill_path.read_text(encoding="utf-8")
            self.assertIn("# Portfolio Risk Compass Agent Protocol", text)
            self.assertNotIn("[README](../../../README.md)", text)
            self.assertIn("[README](", text)

    def test_privacy_scan_reports_locations_without_secret_values(self):
        privacy_scan = load_script("privacy_scan")
        secret = "sk-" + ("a" * 24)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "notes.txt").write_text(f"token={secret}\n", encoding="utf-8")
            output = io.StringIO()

            with redirect_stdout(output):
                result = privacy_scan.main(["--root", str(root)])

            self.assertEqual(result, 1)
            text = output.getvalue()
            self.assertIn("notes.txt:1: openai_key", text)
            self.assertNotIn(secret, text)


if __name__ == "__main__":
    unittest.main()
