import unittest
from dataclasses import astuple

from npm_calmarendian_date import CalmarendianTimeDelta
from npm_calmarendian_date.exceptions import CalmarendianDateError
from npm_calmarendian_date.time_delta import CarryForwardDataBlock


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
            dict(days=0, result=(0, 0, 0)),
            dict(days=1, result=(1, 0, 0)),
            dict(days=1.5, result=(1, 32768, 0)),
            dict(days=1.18838, result=(1, 12345, 671680)),
            dict(days=-1.5, result=(-1, -32768, 0)),
            dict(days=-1.18838, result=(-1, -12345, -671680)),
            dict(days=0.018831229504089355, result=(0, 1234, 123457)),
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                cf = CalmarendianTimeDelta.process_days(item["days"])
                self.assertEqual(item["result"][0], cf.days)
                self.assertEqual(item["result"][1], cf.seconds)
                self.assertEqual(item["result"][2], round(cf.microseconds))

    def test_process_seconds(self):
        def cfb(d: int, s: int, us: float) -> CarryForwardDataBlock:
            return CarryForwardDataBlock(d, s, us)
        data = [
            dict(seconds=0, cf=cfb(0, 0, 0), result=(0, 0, 0)),
            dict(seconds=0, cf=cfb(1, 0, 0), result=(1, 0, 0)),
            dict(seconds=1, cf=cfb(0, 0, 0), result=(0, 1, 0)),
            dict(seconds=1, cf=cfb(1, 0, 0), result=(1, 1, 0)),
            dict(seconds=100, cf=cfb(1, 1000, 0), result=(1, 1100, 0)),
            dict(seconds=-100, cf=cfb(1, 1000, 0), result=(1, 900, 0)),
            dict(seconds=100000, cf=cfb(1, 1000, 500000), result=(1, 101000, 500000)),
            dict(seconds=-100000, cf=cfb(1, 1000, 500000), result=(1, -99000, 500000)),
            dict(seconds=63.5, cf=cfb(1, 1000, 0), result=(1, 1063, 500000)),
            dict(seconds=-100.25, cf=cfb(1, 1000, 0), result=(1, 900, -250000)),
            dict(seconds=-100.25, cf=cfb(1, 1000, 500000), result=(1, 900, 250000)),
            dict(seconds=1111.00000083, cf=cfb(0, 1234, 123456.78), result=(0, 2345, 123458)),
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                cf = CalmarendianTimeDelta.process_seconds(item["seconds"], item["cf"])
                self.assertTupleEqual(item["result"], (cf.days, cf.seconds, round(cf.microseconds)))

    def test_normalization(self):
        def cfb(d: int, s: int, us: float) -> CarryForwardDataBlock:
            return CarryForwardDataBlock(d, s, us)
        data = [
            dict(cf=cfb(0, 0, 0), result=(0, 0, 0)),
            dict(cf=cfb(0, 0, 1), result=(0, 0, 1)),
            dict(cf=cfb(0, 0, 1.7), result=(0, 0, 2)),
            dict(cf=cfb(0, 0, -1), result=(-1, 65535, 999999)),
            dict(cf=cfb(0, 0, 1500000), result=(0, 1, 500000)),
            dict(cf=cfb(0, -65535, 2500000), result=(-1, 3, 500000)),
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                cf = item["cf"]
                cf.normalize()
                self.assertTupleEqual(item["result"], astuple(cf))

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

    def test_bad_microsecond_values(self):
        data = [
            1234.56,  # Final value must be an integer
            -100,
            1_234_567
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                dt = CalmarendianTimeDelta()
                with self.assertRaises(CalmarendianDateError):
                    dt.microseconds = item

    def test_bad_second_values(self):
        data = [
            1234.56,  # Final value must be an integer
            -1,
            1_234_567,
            65_536
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                dt = CalmarendianTimeDelta()
                with self.assertRaises(CalmarendianDateError):
                    dt.seconds = item

    def test_bad_day_values(self):
        data = [
            1234.56,  # Final value must be an integer
            -171_810_101,
            171_810_100,
            200_000_000
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                dt = CalmarendianTimeDelta()
                with self.assertRaises(CalmarendianDateError):
                    dt.days = item


if __name__ == '__main__':
    unittest.main()
