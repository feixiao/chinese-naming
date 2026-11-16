import os
import sys
import json
import subprocess
import unittest

class TestE2EPipeline(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.readme_path = os.path.join(self.base_dir, "README.md")
        self.license_path = os.path.join(self.base_dir, "LICENSE")
        self.cases_path = os.path.join(self.base_dir, "tests", "cases.md")
        self.engine_path = os.path.join(self.base_dir, "scripts", "engine.py")

    def test_open_source_repo_assets_exist(self):
        self.assertTrue(os.path.exists(self.readme_path), "README.md missing")
        self.assertTrue(os.path.exists(self.license_path), "LICENSE missing")
        self.assertTrue(os.path.exists(self.cases_path), "cases.md missing")

        with open(self.readme_path, "r", encoding="utf-8") as f:
            readme = f.read()
        self.assertIn("pm-chinese-naming", readme)
        self.assertIn("/name baby", readme)
        self.assertIn("真太阳时", readme)
        self.assertIn("MIT", readme)

        with open(self.license_path, "r", encoding="utf-8") as f:
            license_text = f.read()
        self.assertIn("MIT License", license_text)

    def test_engine_subprocess_json_execution(self):
        cmd = [
            sys.executable,
            self.engine_path,
            "--date", "2026-08-15 14:30",
            "--city", "杭州",
            "--surname", "陈",
            "--name", "言溪",
            "--json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        self.assertIn("true_solar_time", data)
        self.assertIn("bazi", data)
        self.assertIn("wuxing", data)
        self.assertIn("phonetics", data)
        self.assertEqual(data["phonetics"]["full_name"], "陈言溪")
        self.assertFalse(data["phonetics"]["is_cliche"])
        self.assertFalse(data["phonetics"]["has_homophone_trap"])


if __name__ == "__main__":
    unittest.main()
