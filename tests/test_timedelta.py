import unittest

from npm_calmarendian_date import CalmarendianTimeDelta
from npm_calmarendian_date.exceptions import CalmarendianDateError


class TimeDeltaTest(unittest.TestCase):
    def test_day_time_deltas(self):
        td = CalmarendianTimeDelta(days=1)
        self.assertEqual(1, td.days)
        self.assertEqual(0, td.seconds)
        self.assertEqual(0, td.microseconds)


class TimeDeltaBadDataTest(unittest.TestCase):
    def test_bad_input_types(self):
        with self.assertRaises(CalmarendianDateError):
            td = CalmarendianTimeDelta(seconds='garbage')


if __name__ == '__main__':
    unittest.main()
