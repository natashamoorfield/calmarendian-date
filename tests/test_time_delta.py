import unittest
from dataclasses import astuple

from npm_calmarendian_date import CalmarendianTimeDelta
from npm_calmarendian_date.exceptions import CalmarendianDateError
from npm_calmarendian_date.time_delta import CarryForwardDataBlock

# Let's make a shorthand alias for CalmarendianTimeDelta
Delta = CalmarendianTimeDelta


class TimeDeltaBasicsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dt0 = Delta()
        cls.dt1 = Delta(days=1, seconds=1, microseconds=1)
        cls.dt2 = Delta(days=1, seconds=1, microseconds=1)
        cls.dt3 = Delta(days=-1, seconds=1, microseconds=1)

    def test_get_state(self):
        data = [
            # (test_item, expected)
            (Delta(), (0, 0, 0)),
            (Delta(days=1, seconds=234, microseconds=567), (1, 234, 567)),
        ]
        for index, item in enumerate(data):
            test_item, expected = item
            with self.subTest(i=index):
                self.assertEqual(expected, test_item._get_state())

    def test_compare(self):
        self.assertEqual(0, self.dt1._compare(self.dt2))
        self.assertEqual(1, self.dt1._compare(self.dt0))
        self.assertEqual(-1, self.dt3._compare(self.dt0))
        self.assertEqual(-1, self.dt3._compare(Delta.maximum()))

    def test_eq(self):
        self.assertEqual(self.dt1, self.dt2)
        self.assertNotEqual(self.dt0, self.dt1)
        self.assertNotEqual(self.dt2, "garbage")


class TimeDeltaTest(unittest.TestCase):
    def test_split_float(self):
        data = [
            # (test_item, expected(whole, fractional))
            (1.01, (1, 0.01)),
            (-1.01, (-1, -0.01)),
            (-101.9999999999, (-101, -0.9999999999)),
            (0, (0, 0.0)),
            (-0, (0, 0.0)),
            (11, (11, 0.0)),
            (-20, (-20, 0.0)),
        ]
        for item in data:
            test_item, expected = item
            with self.subTest(i=str(test_item)):
                wp, fp = CalmarendianTimeDelta.split_float(test_item)
                self.assertEqual(expected[0], wp)
                self.assertAlmostEqual(expected[1], fp)
                self.assertIsInstance(wp, int)
                self.assertIsInstance(fp, float)

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

    def test_simple_combinations(self):
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

    def test_combinations_with_carries(self):
        data = [
            # (test_item, expected)
            (Delta(days=100, hours=-1600, minutes=-3, seconds=16, microseconds=176_000_001),
             Delta(microseconds=1)),
            (Delta(days=10.75, hours=24.75, minutes=48, seconds=1.5, microseconds=750_000),
             Delta(days=12, seconds=22530, microseconds=250_000)),
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                self.assertTupleEqual(item[1]._get_state(), item[0]._get_state())

    def test_resolution_info(self):
        delta_max = CalmarendianTimeDelta.maximum()
        delta_min = CalmarendianTimeDelta.minimum()
        delta_res = CalmarendianTimeDelta.resolution()
        self.assertIsInstance(delta_min, CalmarendianTimeDelta)
        self.assertIsInstance(delta_max, CalmarendianTimeDelta)
        self.assertIsInstance(delta_res, CalmarendianTimeDelta)
        # TODO reinstate the next test once comparison methods have been implemented:
        # self.assertTrue(delta_max > delta_min)
        self.assertEqual(str(delta_min), "-171810100 days + 00:00:00.000001")
        self.assertEqual(str(delta_max), "171810099 days + 15:63:63.999999")
        self.assertEqual(str(delta_res), "00:00:00.000001")

    def test_equivalences(self):
        self.assertEqual(Delta(days=1), Delta(hours=16))
        self.assertEqual(Delta(hours=1), Delta(minutes=64))
        self.assertEqual(Delta(minutes=1), Delta(seconds=64))
        self.assertEqual(Delta(seconds=1), Delta(milliseconds=1000))
        self.assertEqual(Delta(milliseconds=1), Delta(microseconds=1000))

        self.assertEqual(Delta(days=1.0/16), Delta(hours=1))
        self.assertEqual(Delta(hours=1.0/64), Delta(minutes=1))
        self.assertEqual(Delta(minutes=1.0/64), Delta(seconds=1))
        self.assertEqual(Delta(seconds=0.001), Delta(milliseconds=1))
        self.assertEqual(Delta(milliseconds=0.001), Delta(microseconds=1))

    def test_total_seconds(self):
        data = [
            # (test_item, expected(int, float))
            (Delta(), (0, 0.00)),
            (Delta(days=1), (65536, 65536.00)),
            (Delta(days=1, seconds=2345), (67881, 67881.00)),
            (Delta(days=1, seconds=2345, microseconds=678900), (67882, 67881.6789)),
            (Delta(days=-1, seconds=2345, microseconds=678900), (-63190, -63190.3211)),
            (Delta(days=100_000_000, seconds=2345, microseconds=678900), (6553600002346, 6553600002345.6789)),
        ]
        for index, item in enumerate(data):
            dt, expected = item
            with self.subTest(i=index):
                self.assertEqual(expected[0], dt.total_seconds('int'))
                self.assertAlmostEqual(expected[1], dt.total_seconds())
                self.assertAlmostEqual(expected[1], dt.total_seconds('float'))


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

    def test_total_seconds(self):
        dt = Delta()
        self.assertRaises(CalmarendianDateError, dt.total_seconds, 'str')


if __name__ == '__main__':
    unittest.main()
