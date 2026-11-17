import os
import re
import unittest

class TestSkillSpec(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.skill_path = os.path.join(self.base_dir, "SKILL.md")

    def test_skill_md_exists_and_valid_frontmatter(self):
        self.assertTrue(os.path.exists(self.skill_path), f"{self.skill_path} does not exist")
        with open(self.skill_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check frontmatter block
        self.assertTrue(content.startswith("---"), "SKILL.md must start with YAML frontmatter ---")
        parts = content.split("---", 2)
        self.assertGreaterEqual(len(parts), 3, "Frontmatter must be enclosed in ---")
        frontmatter = parts[1]

        # Name check
        name_match = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", frontmatter, re.MULTILINE)
        self.assertIsNotNone(name_match, "Frontmatter must contain valid 'name'")
        self.assertEqual(name_match.group(1), "pm-chinese-naming")

        # Description check
        desc_match = re.search(r"^description:\s*(?:>-\s*)?(.*)", frontmatter, re.MULTILINE)
        self.assertIsNotNone(desc_match, "Frontmatter must contain 'description'")
        
        # Check description starts with 'Use this skill when'
        self.assertIn("Use this skill when", frontmatter, "Description must start with 'Use this skill when...'")
        self.assertLessEqual(len(frontmatter), 1024, "Frontmatter must not exceed 1024 chars")

        # Check supported slash commands
        slash_commands = ["/name baby", "/name audit", "/name scaffold"]
        for cmd in slash_commands:
            self.assertIn(cmd, content, f"Missing slash command documentation for {cmd}")
        self.assertNotIn("/name elder", content)

        # Check evidence and safety guardrails
        self.assertIn("不编造诗词", content)
        self.assertIn("真太阳时", content)
        self.assertIn("未命中内置词库", content)
        self.assertNotIn("长辈说服", content)

if __name__ == "__main__":
    unittest.main()
