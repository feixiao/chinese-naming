import os
import json
import unittest

class TestNamingDatasets(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cities_path = os.path.join(self.base_dir, "data", "cities.json")
        self.blacklist_path = os.path.join(self.base_dir, "data", "blacklist.json")

    def test_cities_json_exists_and_valid(self):
        self.assertTrue(os.path.exists(self.cities_path), f"{self.cities_path} does not exist")
        with open(self.cities_path, "r", encoding="utf-8") as f:
            cities = json.load(f)

        self.assertIsInstance(cities, dict)
        self.assertGreaterEqual(len(cities), 340, "Should cover at least 340 prefecture-level cities")

        # Check key major and extreme longitude cities
        major_cities = ["北京", "上海", "广州", "杭州", "成都", "哈尔滨", "乌鲁木齐", "拉萨", "三亚", "喀什"]
        for city in major_cities:
            self.assertIn(city, cities, f"City {city} missing from cities.json")
            entry = cities[city]
            self.assertIn("lng", entry)
            self.assertIn("lat", entry)
            self.assertIn("province", entry)
            # Longitude range for China: ~73E to ~135E
            self.assertGreater(entry["lng"], 73.0)
            self.assertLess(entry["lng"], 136.0)

    def test_blacklist_json_exists_and_valid(self):
        self.assertTrue(os.path.exists(self.blacklist_path), f"{self.blacklist_path} does not exist")
        with open(self.blacklist_path, "r", encoding="utf-8") as f:
            blacklist = json.load(f)

        self.assertIn("cliche_names", blacklist)
        self.assertIn("cliche_characters", blacklist)
        self.assertIn("homophone_traps", blacklist)

        cliche_names = blacklist["cliche_names"]
        self.assertIn("梓涵", cliche_names)
        self.assertIn("子轩", cliche_names)
        self.assertIn("浩宇", cliche_names)
        self.assertIn("雨泽", cliche_names)
        self.assertIn("欣怡", cliche_names)
        self.assertGreaterEqual(len(cliche_names), 50)

if __name__ == "__main__":
    unittest.main()
