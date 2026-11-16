import os
import sys
import json
import unittest
from datetime import datetime

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "scripts"))

import engine


class TestNamingEngine(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(engine, "engine module must be importable")

    def test_true_solar_time(self):
        # Beijing lng: 116.4074 -> offset: (116.4074 - 120) * 4 ~= -14.37 min
        res_bj = engine.calculate_true_solar_time("2026-06-01 12:00", "北京")
        self.assertIn("true_solar_time", res_bj)
        self.assertIn("offset_minutes", res_bj)
        self.assertLess(res_bj["offset_minutes"], 0)

        # Urumqi lng: 87.6177 -> offset: (87.6177 - 120) * 4 ~= -129.5 min (~ -2h 9m)
        res_wlmq = engine.calculate_true_solar_time("2026-06-01 12:00", "乌鲁木齐")
        self.assertLess(res_wlmq["offset_minutes"], -120)
        t_solar = datetime.strptime(res_wlmq["true_solar_time"], "%Y-%m-%d %H:%M:%S")
        self.assertEqual(t_solar.hour, 9)

    def test_bazi_early_and_late_zi_shi(self):
        # 2026-05-10 23:30 (Late Zi-shi) vs 2026-05-11 00:30 (Early Zi-shi)
        dt_late = datetime(2026, 5, 10, 23, 30)
        dt_early = datetime(2026, 5, 11, 0, 30)

        pillars_late = engine.get_bazi_pillars(dt_late)
        pillars_early = engine.get_bazi_pillars(dt_early)

        # Both hour branches should be '子'
        self.assertEqual(pillars_late["hour"][1], "子")
        self.assertEqual(pillars_early["hour"][1], "子")

        # 2026-05-10 is JiaShen (甲申), so hour pillar in Zi-shi is 甲子
        self.assertEqual(pillars_late["hour"], "甲子")

        # Late Zi-shi day pillar belongs to May 10; Early Zi-shi day pillar belongs to May 11
        self.assertNotEqual(pillars_late["day"], pillars_early["day"])
        self.assertEqual(pillars_late["zi_type"], "夜子时")
        self.assertEqual(pillars_early["zi_type"], "早子时")

    def test_wuxing_tiaohou_in_winter(self):
        dt_winter = datetime(2026, 12, 25, 10, 0)
        pillars = engine.get_bazi_pillars(dt_winter)
        analysis = engine.evaluate_wuxing_and_yongshen(pillars)

        self.assertIn("wuxing_counts", analysis)
        self.assertIn("tiaohou", analysis)
        self.assertIn("yongshen", analysis)
        self.assertTrue(any("火" in elem for elem in analysis["tiaohou"]))

    def test_wuxing_tongguan_in_autumn_metal_fire_clash(self):
        # 2026-08-15 14:30 Hangzhou: Month is BingShen (Fire+Metal), Day is XinYou (Metal+Metal), Year is BingWu (Fire+Fire)
        # Metal=3, Fire=3. TongGuan priority is Water (水).
        dt_autumn = datetime(2026, 8, 15, 14, 26)
        pillars = engine.get_bazi_pillars(dt_autumn)
        analysis = engine.evaluate_wuxing_and_yongshen(pillars)

        # Priority element must be Water (水) to reconcile metal and fire
        self.assertEqual(analysis["primary_element"], "水")
        self.assertIn("水", analysis["yongshen"])
        self.assertIn("水", analysis["favorable_radicals"])

    def test_phonetics_and_safety_audit(self):
        # 1. Cliché name test: "陈梓涵"
        res_cliche = engine.audit_phonetics_and_safety("陈", "梓涵")
        self.assertTrue(res_cliche["is_cliche"])
        self.assertIn("梓涵", res_cliche["cliche_matches"])

        # 2. Homophone trap test: "杜子腾"
        res_homo = engine.audit_phonetics_and_safety("杜", "子腾")
        self.assertTrue(res_homo["has_homophone_trap"])
        self.assertEqual(res_homo["homophone_trap"]["homophone"], "肚子疼")

        # 3. Elegant harmonious name test: "陈言溪"
        res_clean = engine.audit_phonetics_and_safety("陈", "言溪")
        self.assertFalse(res_clean["is_cliche"])
        self.assertFalse(res_clean["has_homophone_trap"])
        self.assertFalse(res_clean["has_shuangsheng"])
        self.assertFalse(res_clean["has_dieyun"])
        self.assertTrue(res_clean["is_harmonious"])

    def test_phonetics_shuangsheng_and_dieyun_rejection(self):
        # 双声 (Initial consonant clash): "玲莉" (líng lì, both 'l')
        res_ss = engine.audit_phonetics_and_safety("陈", "玲莉")
        self.assertTrue(res_ss["has_shuangsheng"], "Should detect initial consonant collision (双声)")
        self.assertFalse(res_ss["is_harmonious"], "Shuangsheng should fail harmony check")

        # 叠韵 (Final vowel rhyme clash): "方航" (fāng háng, both 'ang')
        res_dy = engine.audit_phonetics_and_safety("陈", "方航")
        self.assertTrue(res_dy["has_dieyun"], "Should detect final rhyme collision (叠韵)")
        self.assertFalse(res_dy["is_harmonious"], "Dieyun should fail harmony check")

    def test_bazi_dayun_and_gender_calculation(self):
        # 2026 is BingWu (丙午), Stem 丙 is Yang (阳干)
        dt_2026 = datetime(2026, 8, 15, 14, 26)
        pillars_2026 = engine.get_bazi_pillars(dt_2026)
        self.assertEqual(pillars_2026["year"], "丙午")
        self.assertEqual(pillars_2026["month"], "丙申")

        # 1. Male (乾造): Yang stem year -> Forward (顺行)
        dayun_male = engine.calculate_dayun(pillars_2026, gender="男")
        self.assertEqual(dayun_male["gender"], "男")
        self.assertEqual(dayun_male["zaohua"], "乾造")
        self.assertEqual(dayun_male["direction"], "顺行")
        self.assertEqual(dayun_male["pillars"][:4], ["丁酉", "戊戌", "己亥", "庚子"])

        # 2. Female (坤造): Yang stem year -> Backward (逆行)
        dayun_female = engine.calculate_dayun(pillars_2026, gender="女")
        self.assertEqual(dayun_female["gender"], "女")
        self.assertEqual(dayun_female["zaohua"], "坤造")
        self.assertEqual(dayun_female["direction"], "逆行")
        self.assertEqual(dayun_female["pillars"][:4], ["乙未", "甲午", "癸巳", "壬辰"])

    def test_cli_full_pipeline(self):
        res = engine.run_full_audit(
            date_str="2026-08-15 14:30",
            city="杭州",
            surname="陈",
            given_name="言溪",
            gender="女"
        )
        self.assertIn("true_solar_time", res)
        self.assertIn("bazi", res)
        self.assertIn("dayun", res)
        self.assertEqual(res["dayun"]["zaohua"], "坤造")
        self.assertEqual(res["dayun"]["direction"], "逆行")
        self.assertIn("wuxing", res)
        self.assertIn("phonetics", res)
        self.assertIn("radar_scores", res)
        self.assertIn("suggested_elements", res)
        self.assertIn("水", res["suggested_elements"])


if __name__ == "__main__":
    unittest.main()
