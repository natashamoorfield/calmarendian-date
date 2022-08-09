import unittest
from dataclasses import astuple

from npm_calmarendian_date import (
    split_float,
    round_half_away_from_zero
)
from npm_calmarendian_date.c_date_utils import DateTimeStruct


class UtilitiesTest(unittest.TestCase):
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
                wp, fp = split_float(test_item)
                self.assertEqual(expected[0], wp)
                self.assertAlmostEqual(expected[1], fp)
                self.assertIsInstance(wp, int)
                self.assertIsInstance(fp, float)

    def test_round_half_away_from_zero(self):
        data = [
            (0, 0),
            (0.0, 0),
            (0.25, 0),
            (-0.25, 0),
            (0.5, 1),
            (-0.5, -1),
            (0.75, 1),
            (-0.75, -1),
            (1.5, 2),
            (-1.5, -2),
            (-2, -2),
        ]
        for index, item in enumerate(data):
            test_item, expected = item
            test_item = round_half_away_from_zero(test_item)
            with self.subTest(i=index):
                self.assertEqual(expected, test_item)
                self.assertIsInstance(test_item, int)


class DateTimeStructTests(unittest.TestCase):
    def test_basic_instantiation(self):
        data = [
            (DateTimeStruct(2, 77, 7, 7, 7, 0, 1, 23, 456789, -2), (2, 77, 7, 7, 7, 0, 1, 23, 456789, -2)),
            (DateTimeStruct(2, 34, 5, 6, 7), (2, 34, 5, 6, 7, 0, 0, 0, 0, 0)),
            (DateTimeStruct(2, 34, 5, 6, 17), (2, 34, 5, 6, 17, 0, 0, 0, 0, 0)),  # Works with junk values
        ]
        for index, item in enumerate(data):
            test_item, expected = item
            with self.subTest(i=index):
                self.assertTupleEqual(expected, astuple(test_item))


if __name__ == '__main__':
    unittest.main()
