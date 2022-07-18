import unittest

from npm_calmarendian_date import CalmarendianTimeDelta
from npm_calmarendian_date.exceptions import CalmarendianDateError


class TimeDeltaTest(unittest.TestCase):
    def test_split_float(self):
        data = [
            {"input": 1.01, "output": (1, 0.01)},
            {"input": -1.01, "output": (-1, -0.01)},
            {"input": -101.9999999999, "output": (-101, -0.9999999999)},
            {"input": 0, "output": (0, 0.0)},
            {"input": 10, "output": (10, 0.0)},
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                fx = CalmarendianTimeDelta.split_float(item["input"])
                self.assertEqual(item["output"][0], fx[0])
                self.assertAlmostEqual(item["output"][1], fx[1])
                self.assertIsInstance(fx[0], int)
                self.assertIsInstance(fx[1], float)

    def test_process_days(self):
        data = [
            dict(days=0, result=(0, 0, 0.00, 0, 0.00)),
            dict(days=1, result=(1, 0, 0.00, 0, 0.00)),
            dict(days=1.5, result=(1, 32768, 0.0, 0, 0.0)),
            dict(days=1.18837997436523438, result=(1, 12345, 0.67, 0, 0.0)),
            dict(days=-1.5, result=(-1, -32768, 0.0, 0, 0.0)),
            dict(days=-1.18837997436523438, result=(-1, -12345, -0.67, 0, 0.0)),
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                cf = CalmarendianTimeDelta.process_days(item["days"])
                self.assertEqual(item["result"][0], cf.days)
                self.assertEqual(item["result"][1], cf.whole_seconds)
                self.assertEqual(item["result"][3], cf.whole_microseconds)
                self.assertAlmostEqual(item["result"][2], cf.fractional_seconds, 7)
                self.assertAlmostEqual(item["result"][4], cf.fractional_microseconds, 2)

    def test_day_time_deltas(self):
        data = [
            {"input": {"days": 1},
             "output": (1, 0, 0, "1 day + 00:00:00")},
            {"input": {},
             "output": (0, 0, 0, "00:00:00")},
            {"input": {"days": -1},
             "output": (-1, 0, 0, "-1 day + 00:00:00")},
            {"input": {"days": 1.5},
             "output": (1, 32768, 0, "1 day + 08:00:00")},
            {"input": {"days": -1.5},
             "output": (-2, 32768, 0, "-2 days + 08:00:00")},
        ]
        for key, item in enumerate(data):
            with self.subTest(i=key):
                td = CalmarendianTimeDelta(**item["input"])
                self.assertEqual(item["output"], (td.days, td.seconds, td.microseconds, str(td)))

    def test_seconds_time_deltas(self):
        data = [
            {"input": {"seconds": -1},
             "output": (-1, 65535, 0, "-1 day + 15:63:63")},
            {"input": {"seconds": 1},
             "output": (0, 1, 0, "00:00:01")},
            {"input": {"seconds": 1054.15000026},
             "output": (0, 1054, 150000, "00:16:30.150000")},
            {"input": {"seconds": 1054.15000076},
             "output": (0, 1054, 150001, "00:16:30.150001")},
            {"input": {"hours": 1.2, "seconds": -3861.04999924},
             "output": (0, 1054, 150001, "00:16:30.150001")},
        ]
        for key, item in enumerate(data):
            with self.subTest(i=key):
                td = CalmarendianTimeDelta(**item["input"])
                self.assertEqual(item["output"], (td.days, td.seconds, td.microseconds, str(td)))

    def test_combination_time_deltas(self):
        data = [
            {"input": {"days": 1, "hours": 8},
             "output": (1, 32768, 0, "1 day + 08:00:00")},
            {"input": {"days": 1, "minutes": 512},
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
