import unittest
from npm_calmarendian_date import (
    split_float
)


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


if __name__ == '__main__':
    unittest.main()
