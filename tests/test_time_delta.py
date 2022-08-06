import unittest
from dataclasses import astuple

from npm_calmarendian_date import CalmarendianTimeDelta, CalmarendianDate
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

    def test_str(self):
        data = [
            (Delta(days=-2), "-2 days + 00:00:00"),
            (Delta(days=-2, seconds=45771), "-2 days + 11:11:11"),
            (Delta(days=-2, seconds=45771, microseconds=222000), "-2 days + 11:11:11.222000"),
            (Delta(days=-1), "-1 day + 00:00:00"),
            (self.dt3, "-1 day + 00:00:01.000001"),
            (self.dt0, "00:00:00"),
            (Delta(milliseconds=1), "00:00:00.001000"),
            (Delta(days=0, seconds=5568), "01:23:00"),
            (Delta(seconds=51384), "12:34:56"),
            (Delta(days=1), "+1 day + 00:00:00"),
            (Delta(days=2), "+2 days + 00:00:00"),
            (self.dt1, "+1 day + 00:00:01.000001"),
            (Delta(days=+2, seconds=28672), "+2 days + 07:00:00"),
            (Delta(days=2, seconds=448), "+2 days + 00:07:00"),
            (Delta(days=2, seconds=45771), "+2 days + 11:11:11"),
            (Delta(days=2, seconds=45771, microseconds=222000), "+2 days + 11:11:11.222000"),
        ]
        for item in data:
            test_item, expected = item
            with self.subTest(dt=expected):
                self.assertEqual(expected, str(test_item))


class TimeDeltaTest(unittest.TestCase):
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
                # assertAlmostEqual dose not always cut the mustard.
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
                # assertAlmostEqual dose not always cut the mustard.
                self.assertTupleEqual(item["result"], (cf.days, cf.seconds, round(cf.microseconds)))

    def test_normalization(self):
        def cfb(d: int, s: int, us: float) -> CarryForwardDataBlock:
            return CarryForwardDataBlock(d, s, us)

        data = [
            dict(cf=cfb(0, 0, 0), result=(0, 0, 0)),
            dict(cf=cfb(0, 0, 1), result=(0, 0, 1)),
            dict(cf=cfb(0, 0, 1.7), result=(0, 0, 2)),
            dict(cf=cfb(0, 0, 2.5), result=(0, 0, 3)),
            dict(cf=cfb(0, 0, -1), result=(-1, 65535, 999999)),
            dict(cf=cfb(0, 0, 1500000), result=(0, 1, 500000)),
            dict(cf=cfb(0, -65535, 2500000), result=(-1, 3, 500000)),
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                cf = item["cf"]
                cf.normalize()
                self.assertTupleEqual(item["result"], astuple(cf))

    def test_microsecond_rounding(self):
        """
        Do not forget that we are using round halves away from zero...
        """
        data = [
            (Delta(), 0),
            (Delta(milliseconds=0.4 / 1000), 0),
            (Delta(milliseconds=-0.4 / 1000), 0),
            (Delta(milliseconds=0.5 / 1000), 1),  # Round half away from zero
            (Delta(milliseconds=-0.5 / 1000), -1),  # Round half away from zero
            (Delta(milliseconds=0.6 / 1000), 1),
            (Delta(milliseconds=-0.6 / 1000), -1),
            (Delta(milliseconds=1.5 / 1000), 2),  # Round half away from zero
            (Delta(milliseconds=-1.5 / 1000), -2),  # Round half away from zero
            (Delta(seconds=0.5 / 1_000_000), 1),
            (Delta(seconds=-0.5 / 1_000_000), -1),
            (Delta(seconds=1 / 128), 7813),
            (Delta(seconds=-1 / 128), -7813),
            (Delta(days=0.25 / 65_536_000_000), 0),
            (Delta(days=0.5 / 65_536_000_000), 1),
            (Delta(days=0.75 / 65_536_000_000), 1),
            (Delta(days=-0.25 / 65_536_000_000), 0),
            (Delta(days=-0.5 / 65_536_000_000), -1),
            (Delta(days=-0.75 / 65_536_000_000), -1),
            (Delta(seconds=1.234_567_8, microseconds=31.8), 1_234_600),
            (Delta(days=1.234_567_8 / 65536, microseconds=31.8), 1_234_600),
            (Delta(days=1.234_567_8 / 65536, seconds=1.234_567_8), 2_469_136),
        ]
        for index, item in enumerate(data):
            test_item: Delta = item[0]
            expected = Delta(microseconds=item[1])
            with self.subTest(i=index):
                self.assertEqual(expected, test_item)

    def test_day_time_deltas(self):
        data = [
            {"input": {"days": 1},
             "output": (1, 0, 0, "+1 day + 00:00:00")},
            {"input": {},
             "output": (0, 0, 0, "00:00:00")},
            {"input": {"days": -1},
             "output": (-1, 0, 0, "-1 day + 00:00:00")},
            {"input": {"days": 1.5},
             "output": (1, 32768, 0, "+1 day + 08:00:00")},
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
             "output": (1, 32768, 0, "+1 day + 08:00:00")},
            {"input": {"days": 1, "minutes": 512},
             "output": (1, 32768, 0, "+1 day + 08:00:00")},
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
        self.assertTrue(delta_max > delta_min)
        self.assertEqual(str(delta_min), "-171,810,100 days + 00:00:00.000001")
        self.assertEqual(str(delta_max), "+171,810,099 days + 15:63:63.999999")
        self.assertEqual(str(delta_res), "00:00:00.000001")

    def test_equivalences(self):
        self.assertEqual(Delta(days=1), Delta(hours=16))
        self.assertEqual(Delta(hours=1), Delta(minutes=64))
        self.assertEqual(Delta(minutes=1), Delta(seconds=64))
        self.assertEqual(Delta(seconds=1), Delta(milliseconds=1000))
        self.assertEqual(Delta(milliseconds=1), Delta(microseconds=1000))

        self.assertEqual(Delta(days=1.0 / 16), Delta(hours=1))
        self.assertEqual(Delta(hours=1.0 / 64), Delta(minutes=1))
        self.assertEqual(Delta(minutes=1.0 / 64), Delta(seconds=1))
        self.assertEqual(Delta(seconds=0.001), Delta(milliseconds=1))
        self.assertEqual(Delta(milliseconds=0.001), Delta(microseconds=1))

    def test_bool(self):
        self.assertTrue(Delta(days=1))
        self.assertTrue(Delta(seconds=1))
        self.assertTrue(Delta(microseconds=1))
        self.assertTrue(Delta(microseconds=-1))
        self.assertFalse(Delta())
        self.assertFalse(Delta(days=0.0))

    def test_compare_equal_objects(self):
        dt1 = Delta(days=1, seconds=234, microseconds=567890)
        dt2 = Delta(days=1, seconds=234, microseconds=567890)
        self.assertEqual(dt1, dt2)
        self.assertTrue(dt1 <= dt2)
        self.assertTrue(dt1 >= dt2)
        self.assertFalse(dt1 != dt2)
        self.assertFalse(dt1 < dt2)
        self.assertFalse(dt1 > dt2)

    def test_compare_unequal_objects(self):
        dt1 = Delta(days=1, seconds=234, microseconds=567890)
        data = [
            Delta(days=12, seconds=234, microseconds=567890),
            Delta(days=1, seconds=2345, microseconds=567890),
            Delta(days=1, seconds=234, microseconds=678900),
        ]
        for dt2 in data:
            self.assertTrue(dt1 < dt2)
            self.assertTrue(dt2 > dt1)
            self.assertTrue(dt1 <= dt2)
            self.assertTrue(dt2 >= dt1)
            self.assertTrue(dt1 != dt2)
            self.assertTrue(dt2 != dt1)
            self.assertFalse(dt1 == dt2)
            self.assertFalse(dt2 == dt1)
            self.assertFalse(dt1 > dt2)
            self.assertFalse(dt2 < dt1)
            self.assertFalse(dt1 >= dt2)
            self.assertFalse(dt2 <= dt1)

    def test_total_seconds(self):
        data = [
            # (test_item, expected(int, float))
            (Delta(), (0, 0.00)),
            (Delta(days=1), (65536, 65536.00)),
            (Delta(days=1, seconds=2345), (67881, 67881.00)),
            (Delta(days=1, seconds=2345, microseconds=678900), (67882, 67881.6789)),
            (Delta(days=-1, seconds=2345, microseconds=678900), (-63190, -63190.3211)),
            (Delta(days=1, seconds=2345, microseconds=321100), (67881, 67881.3211)),
            (Delta(days=-1, seconds=2345, microseconds=321100), (-63191, -63190.6789)),
            (Delta(days=1, seconds=2345, microseconds=500_000), (67882, 67881.5)),
            (Delta(days=-1, seconds=2345, microseconds=500_000), (-63191, -63190.5)),
            (Delta(days=100_000_000, seconds=2345, microseconds=678900), (6553600002346, 6553600002345.6789)),
        ]
        for index, item in enumerate(data):
            dt, expected = item
            with self.subTest(i=index):
                self.assertEqual(expected[0], dt.total_seconds('int'))
                self.assertAlmostEqual(expected[1], dt.total_seconds())
                self.assertAlmostEqual(expected[1], dt.total_seconds('float'))

    def test_object_hashing(self):
        data = [
            # (test_item, expected)
            (Delta(days=200, hours=-3200, minutes=-3, seconds=16, microseconds=176_000_000),
             Delta()),
            (Delta(days=10.75, hours=24.75, minutes=48, seconds=1.5, microseconds=750_000),
             Delta(days=12, seconds=22530, microseconds=250_000)),
        ]
        for index, item in enumerate(data):
            dt1, dt2 = item
            dx = {dt1: 1}
            with self.subTest(i=index):
                self.assertEqual(hash(dt2), hash(dt1))
                dx[dt2] = 2
                self.assertEqual(1, len(dx))
                self.assertEqual(2, dx[dt1])

    def test_repr(self):
        data = [
            (Delta(), ''),
            (Delta(days=12), 'days=12'),
            (Delta(seconds=23), 'seconds=23'),
            (Delta(microseconds=567890), 'microseconds=567890'),
            (Delta(days=12, seconds=34), 'days=12, seconds=34'),
            (Delta(days=12, microseconds=567890), 'days=12, microseconds=567890'),
            (Delta(seconds=34, microseconds=0), 'seconds=34'),
            (Delta(days=12, seconds=34, microseconds=567890), 'days=12, seconds=34, microseconds=567890'),
            (Delta(seconds=65_536), 'days=1')
        ]
        for index, item in enumerate(data):
            test_item_repr = repr(item[0])
            expected = f"CalmarendianTimeDelta({item[1]})"
            with self.subTest(i=index):
                self.assertTrue(test_item_repr.startswith("CalmarendianTimeDelta"))
                self.assertEqual(expected, test_item_repr)

    def test_new_from_repr(self):
        data = [
            Delta(days=1, seconds=2345, microseconds=678900),
            Delta.maximum(),
            Delta.minimum(),
            Delta(days=-171_810_100, seconds=1),
            Delta(microseconds=-1)
        ]
        for index, test_item in enumerate(data):
            with self.subTest(i=index):
                self.assertEqual(test_item, eval(repr(test_item)))


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

    def test_illegal_assignments(self):
        dt = Delta(days=1, seconds=23, microseconds=45678)
        dx = {dt: 0}
        with self.assertRaises(CalmarendianDateError):
            dt.days = 99
        with self.assertRaises(CalmarendianDateError):
            dt.seconds -= 99
        with self.assertRaises(CalmarendianDateError):
            dt.days += 99
        self.assertEqual(0, dx[dt])

    def test_bad_comparisons(self):
        junk_data = [
            123,
            123.456,
            complex(123, 456),
            (),
            [],
            {},
            "junk string",
            CalmarendianDate(1234567)
        ]
        dt1 = Delta(days=12, seconds=22530, microseconds=250_000)

        for garbage in junk_data:
            self.assertEqual(dt1 == garbage, False)
            self.assertEqual(dt1 != garbage, True)
            self.assertEqual(garbage == dt1, False)
            self.assertEqual(garbage != dt1, True)

            self.assertRaises(TypeError, lambda: dt1 <= garbage)
            self.assertRaises(TypeError, lambda: dt1 < garbage)
            self.assertRaises(TypeError, lambda: dt1 > garbage)
            self.assertRaises(TypeError, lambda: dt1 >= garbage)
            self.assertRaises(TypeError, lambda: garbage <= dt1)
            self.assertRaises(TypeError, lambda: garbage < dt1)
            self.assertRaises(TypeError, lambda: garbage > dt1)
            self.assertRaises(TypeError, lambda: garbage >= dt1)


if __name__ == '__main__':
    unittest.main()
