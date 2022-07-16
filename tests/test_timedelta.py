import unittest

from npm_calmarendian_date import CalmarendianTimeDelta
from npm_calmarendian_date.exceptions import CalmarendianDateError


class TimeDeltaTest(unittest.TestCase):
    def test_day_time_deltas(self):
        data = [
            {"input": {"days": 1},
             "output": (1, 0, 0, "1 day + 00:00:00")},
            {"input": {},
             "output": (0, 0, 0, "00:00:00")},
            {"input": {"days": -1},
             "output": (-1, 0, 0, "-1 days + 00:00:00")},
            {"input": {"days": 1.5},
             "output": (1, 32768, 0, "1 day + 08:00:00")},
        ]
        for key, item in enumerate(data):
            with self.subTest(i=key):
                td = CalmarendianTimeDelta(**item["input"])
                self.assertEqual(item["output"], (td.days, td.seconds, td.microseconds, str(td)))


class TimeDeltaBadDataTest(unittest.TestCase):
    def test_bad_input_types(self):
        data = [
            {"days": "garbage"},
            {"hours": "garbage"},
            {"minutes": "garbage"},
            {"seconds": complex(12)},
            {"milliseconds": "69"},
            {"microseconds": ["garbage"]},
        ]
        for key, item in enumerate(data):
            with self.subTest(i=key):
                with self.assertRaises(CalmarendianDateError):
                    CalmarendianTimeDelta(**item)


if __name__ == '__main__':
    unittest.main()
