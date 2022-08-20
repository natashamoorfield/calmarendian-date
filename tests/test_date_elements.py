import unittest

from npm_calmarendian_date.date_elements import GrandCycle, CycleInGrandCycle, Season, Week, Day
from npm_calmarendian_date.exceptions import CalmarendianDateError, CalmarendianDateFormatError


class GrandCycleTest(unittest.TestCase):
    def test_bad_grand_cycle_input(self):
        with self.assertRaises(CalmarendianDateError):
            GrandCycle(-10)
        with self.assertRaises(CalmarendianDateError):
            GrandCycle(-1)
        with self.assertRaises(CalmarendianDateError):
            GrandCycle(100)

    def test_error_messages(self):
        with self.assertRaisesRegex(CalmarendianDateError, "GRAND CYCLE: -1"):
            GrandCycle(-1)
        with self.assertRaisesRegex(CalmarendianDateError, "GRAND CYCLE: 200"):
            GrandCycle(200)

    def test_good_grand_cycle_input(self):
        items = [
            {"input": {"grand_cycle": 0}, "result": 0},
            {"input": {"grand_cycle": 1}, "result": 1},
            {"input": {"grand_cycle": 9}, "result": 9},
            {"input": {"grand_cycle": 99}, "result": 99},
        ]
        for item in items:
            d = GrandCycle(**item["input"])
            self.assertEqual(item["result"], d.number)

    def test_grand_cycle_days_prior(self):
        items = [
            {"input": {"grand_cycle": 0}, "result": -1_718_101},
            {"input": {"grand_cycle": 1}, "result": 0},
            {"input": {"grand_cycle": 9}, "result": 13_744_808},
            {"input": {"grand_cycle": 99}, "result": 168_373_898},
        ]
        for item in items:
            d = GrandCycle(**item["input"])
            self.assertEqual(item["result"], d.days_prior())


class CycleInGrandCycleTest(unittest.TestCase):
    def test_bad_cycle_input(self):
        with self.assertRaises(CalmarendianDateError):
            CycleInGrandCycle(-10)
        with self.assertRaises(CalmarendianDateError):
            CycleInGrandCycle(0)
        with self.assertRaises(CalmarendianDateError):
            CycleInGrandCycle(701)

    def test_error_messages(self):
        with self.assertRaisesRegex(CalmarendianDateError, "CYCLE in GRAND CYCLE: 999"):
            CycleInGrandCycle(999)
        with self.assertRaisesRegex(CalmarendianDateError, "0 is an invalid input"):
            CycleInGrandCycle(0)

    def test_good_cycle_input(self):
        items = [
            {"input": {"cycle": 1}, "result": 1},
            {"input": {"cycle": 300}, "result": 300},
            {"input": {"cycle": 700}, "result": 700},
        ]
        for item in items:
            d = CycleInGrandCycle(**item["input"])
            self.assertEqual(item["result"], d.number)

    def test_festival_days_calculation(self):
        items = [
            {"input": {"cycle": 6}, "result": 4},
            {"input": {"cycle": 666}, "result": 4},
            {"input": {"cycle": 700}, "result": 8},
            {"input": {"cycle": 7}, "result": 7},
            {"input": {"cycle": 315}, "result": 7},
        ]
        for item in items:
            d = CycleInGrandCycle(**item["input"])
            self.assertEqual(item["result"], d.festival_days())

    def test_days_prior_encode(self):
        items = [
            {"input": {"cycle": 1}, "result": 0},
            {"input": {"cycle": 2}, "result": 2454},
            {"input": {"cycle": 3}, "result": 4908},
            {"input": {"cycle": 7}, "result": 14_724},
            {"input": {"cycle": 8}, "result": 17_181},
            {"input": {"cycle": 100}, "result": 242_988},
            {"input": {"cycle": 258}, "result": 630_786},
            {"input": {"cycle": 699}, "result": 1_713_189},
            {"input": {"cycle": 700}, "result": 1_715_643},
        ]
        for item in items:
            d = CycleInGrandCycle(**item["input"])
            self.assertEqual(item["result"], d.days_prior())


class SeasonTest(unittest.TestCase):
    def test_bad_season_input_too_small(self):
        with self.assertRaises(CalmarendianDateError):
            Season(-10)
        with self.assertRaises(CalmarendianDateError):
            Season(-1)

    def test_bad_season_input_too_big(self):
        with self.assertRaises(CalmarendianDateError):
            Season(8)
        with self.assertRaises(CalmarendianDateError):
            Season(700)

    def test_error_messages(self):
        with self.assertRaisesRegex(CalmarendianDateError, "SEASON: 0"):
            Season(0)
        with self.assertRaisesRegex(CalmarendianDateError, "10 is an invalid input"):
            Season(10)

    def test_good_season_input(self):
        for i in range(1, 8):
            s = Season(i)
            self.assertEqual(i, s.number)

    def test_season_max_weeks(self):
        data = [
            {"season": 1, "result": 50},
            {"season": 6, "result": 50},
            {"season": 7, "result": 51},
        ]
        for item in data:
            s = Season(item["season"])
            self.assertEqual(item["result"], s.max_weeks())

    def test_season_days_prior(self):
        data = [
            {"season": 1, "result": 0},
            {"season": 2, "result": 350},
            {"season": 5, "result": 1400},
            {"season": 7, "result": 2100},
        ]
        for item in data:
            d = Season(item["season"])
            self.assertEqual(item["result"], d.days_prior())

    def test_from_name(self):
        data = [
            ("M", 1),
            ("th", 2),
            ("sPR", 3),
            ("Perihelion", 4),
            ("high summer", 5),
            ("a", 6),
            ("Ons", 7),
            ("7", 7),
        ]
        for item in data:
            test_input, expected = item
            with self.subTest(i=test_input):
                self.assertEqual(expected, Season.from_name(test_input).number)

    def test_from_bad_name(self):
        data = [
            (6, "SEASON: Name must be 'str', not 'int'."),
            ([7], "SEASON: Name must be 'str', not 'list'."),
            ("", "SEASON: Name cannot be an empty string."),
            ("Z", "SEASON: Name 'Z' not recognized."),
            ("Thaws", "SEASON: Name 'Thaws' not recognized."),
            ("Summer", "SEASON: Name 'Summer' not recognized."),
            ("8", "SEASON: If specified numerically must be between 1 and 7, not 8.")
        ]
        for index, item in enumerate(data):
            test_input, expected = item
            with self.subTest(i=index):
                with self.assertRaises(CalmarendianDateFormatError) as cm:
                    Season.from_name(test_input)
                self.assertEqual(expected, cm.exception.__str__())


class WeekTest(unittest.TestCase):
    def test_week_too_small(self):
        with self.assertRaises(CalmarendianDateError):
            Week(-1, Season(4))
        with self.assertRaises(CalmarendianDateError):
            Week(0, Season(5))

    def test_week_too_big(self):
        with self.assertRaises(CalmarendianDateError):
            Week(51, Season(6))
        with self.assertRaises(CalmarendianDateError):
            Week(52, Season(7))

    def test_error_messages(self):
        with self.assertRaisesRegex(CalmarendianDateError, "WEEK: 52.*season 7.*1 and 51"):
            Week(52, Season(7))
        with self.assertRaisesRegex(CalmarendianDateError, "WEEK: 51.*season 6.*1 and 50"):
            Week(51, Season(6))
        with self.assertRaisesRegex(CalmarendianDateError, "WEEK: 0.*season 7.*1 and 51"):
            Week(0, Season(7))

    def test_good_week(self):
        data = [
            {"input": {"week": 1, "season": Season(1)}, "result": 1},
            {"input": {"week": 50, "season": Season(2)}, "result": 50},
            {"input": {"week": 51, "season": Season(7)}, "result": 51},
        ]
        for item in data:
            w = Week(**item["input"])
            self.assertEqual(item["result"], w.number)

    def test_week_days_prior(self):
        data = [
            {"week": 1, "season": 6, "result": 0},
            {"week": 1, "season": 7, "result": 0},
            {"week": 2, "season": 5, "result": 7},
            {"week": 22, "season": 4, "result": 147},
            {"week": 50, "season": 4, "result": 343},
            {"week": 51, "season": 7, "result": 350},
        ]
        for item in data:
            d = Week(item["week"], Season(item["season"]))
            self.assertEqual(item["result"], d.days_prior())


class DayTest(unittest.TestCase):
    def test_bad_day_too_small(self):
        with self.assertRaises(CalmarendianDateError):
            Day(day=0, week=Week(10, Season(4)), cycle=CycleInGrandCycle(10))

    def test_bad_day_too_big_std(self):
        with self.assertRaises(CalmarendianDateError):
            Day(day=8, week=Week(10, Season(4)), cycle=CycleInGrandCycle(10))

    def test_bad_day_too_big_f4(self):
        with self.assertRaises(CalmarendianDateError):
            Day(day=5, week=Week(51, Season(7)), cycle=CycleInGrandCycle(75))

    def test_bad_day_too_big_f7(self):
        with self.assertRaises(CalmarendianDateError):
            Day(day=8, week=Week(51, Season(7)), cycle=CycleInGrandCycle(77))

    def test_bad_day_too_big_f8(self):
        with self.assertRaises(CalmarendianDateError):
            Day(day=9, week=Week(51, Season(7)), cycle=CycleInGrandCycle(700))

    def test_error_messages(self):
        data = [
            (
                "DAY must be in [1 .. 7] for specified week; not 0",
                0, 12, 4, 100
            ),
            (
                "DAY must be in [1 .. 7] for specified week; not 8",
                8, 14, 5, 108
            ),
            (
                "DAY must be in [1 .. 4] for specified week; not 5",
                5, 51, 7, 177
            ),
            (
                "DAY must be in [1 .. 7] for specified week; not 8",
                8, 51, 7, 175
            ),
            (
                "DAY must be in [1 .. 8] for specified week; not 9",
                9, 51, 7, 700
            ),
        ]
        for i in data:
            with self.subTest(i=i[1:]):
                with self.assertRaises(CalmarendianDateError) as cm:
                    Day(day=i[1], week=Week(i[2], Season(i[3])), cycle=CycleInGrandCycle(i[4]))
                self.assertEqual(i[0], cm.exception.__str__())

    def test_good_days_standard(self):
        data = [
            {"input": {"day": 1, "week": Week(10, Season(3)), "cycle": CycleInGrandCycle(10)}, "result": 1},
            {"input": {"day": 7, "week": Week(10, Season(4)), "cycle": CycleInGrandCycle(10)}, "result": 7},
            {"input": {"day": 7, "week": Week(50, Season(5)), "cycle": CycleInGrandCycle(77)}, "result": 7},
        ]
        for item in data:
            d = Day(**item["input"])
            self.assertEqual(item["result"], d.number)

    def test_good_days_festival(self):
        data = [
            {"input": {"day": 4, "week": Week(51, Season(7)), "cycle": CycleInGrandCycle(75)}, "result": 4},
            {"input": {"day": 7, "week": Week(51, Season(7)), "cycle": CycleInGrandCycle(70)}, "result": 7},
            {"input": {"day": 8, "week": Week(51, Season(7)), "cycle": CycleInGrandCycle(700)}, "result": 8},
        ]
        for item in data:
            d = Day(**item["input"])
            self.assertEqual(item["result"], d.number)


class WeekNamesTest(unittest.TestCase):
    def test_for_duplicates(self):
        self.assertEqual(len(Week.WEEK_NAMES), len(set(Week.WEEK_NAMES)))

    def test_raw_list_access(self):
        # Don't forget the offset by one...
        self.assertEqual('Saponaria', Week.WEEK_NAMES[0])
        self.assertEqual('Zenobia', Week.WEEK_NAMES[5])
        self.assertEqual('Daisy', Week.WEEK_NAMES[13])
        self.assertEqual('Heliotrope', Week.WEEK_NAMES[49])
        self.assertEqual('Festival', Week.WEEK_NAMES[50])

    def test_access_method(self):
        data = [
            {"input": {"week": 1, "season": Season(1)}, "result": "Saponaria"},
            {"input": {"week": 50, "season": Season(2)}, "result": "Heliotrope"},
            {"input": {"week": 51, "season": Season(7)}, "result": "Festival"},
        ]
        for item in data:
            w = Week(**item["input"])
            self.assertEqual(item["result"], w.name())


class WeekendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = [
            {"input": {"week": 1, "season": Season(1)}, "result": ("Short", 2.0)},
            {"input": {"week": 5, "season": Season(7)}, "result": ("Long", 3.0)},
            {"input": {"week": 25, "season": Season(2)}, "result": ("Mid-Season", 3.5)},
            {"input": {"week": 50, "season": Season(3)}, "result": ("Heliotrope", 3.5)},
            {"input": {"week": 50, "season": Season(7)}, "result": ("Festival", 3.5)},
            {"input": {"week": 51, "season": Season(7)}, "result": ("", 0.0)},
        ]

    def test_base_weekend_method(self):
        for item in self.data:
            w = Week(**item['input'])
            week_ident = f'S{w.season.number} W{w.number}'
            with self.subTest(i=week_ident):
                self.assertEqual(item['result'], w.weekend)

    def test_weekend_descriptor(self):
        for item in self.data:
            w = Week(**item['input'])
            week_ident = f'S{w.season.number} W{w.number}'
            with self.subTest(i=week_ident):
                self.assertEqual(item['result'][0], w.weekend.descriptor)

    def test_weekend_length(self):
        for item in self.data:
            w = Week(**item['input'])
            week_ident = f'S{w.season.number} W{w.number}'
            with self.subTest(i=week_ident):
                self.assertEqual(item['result'][1], w.weekend.duration)


if __name__ == '__main__':
    unittest.main()
