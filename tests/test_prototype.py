import os
import unittest

class TestPrototypeHTML(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.html_path = os.path.join(self.base_dir, "prototypes", "naming-card.html")

    def test_prototype_exists_and_conforms(self):
        self.assertTrue(os.path.exists(self.html_path), f"{self.html_path} does not exist")
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check PM Debug bar
        self.assertTrue("PM 评审状态切换器" in content or "PM 状态切换器" in content, "Must contain PM state switcher")

        # Check supported states are represented in the DOM
        self.assertIn("state-normal", content)
        self.assertIn("state-empty", content)
        self.assertIn("state-loading", content)
        self.assertIn("state-blocked", content)
        self.assertNotIn("state-elder", content)

        # Check visual elements
        self.assertIn("<svg", content, "Must include SVG elements for radar chart / visuals")
        self.assertNotIn("长辈说服卡", content)
        self.assertIn("真太阳时", content)
        self.assertIn("八字", content)

        # Check offline resilience: must have .hidden rule in <style>
        self.assertIn(".hidden {", content)
        self.assertIn("display: none !important;", content)

        # Check self-contained / no broken local relative script/css
        self.assertNotIn('href="./style.css"', content)
        self.assertNotIn('src="./app.js"', content)

if __name__ == "__main__":
    unittest.main()
