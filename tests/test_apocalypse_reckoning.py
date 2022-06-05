import unittest

from npm_calmarendian_date import CalmarendianDate
from npm_calmarendian_date.c_date_config import CDateConfig


class ARTest(unittest.TestCase):
    def test_ar_epoch(self):
        ar0 = CalmarendianDate(CDateConfig.APOCALYPSE_EPOCH_ADR)
        self.assertEqual(CalmarendianDate.from_date_string('777-7-02-7'), ar0)


if __name__ == '__main__':
    unittest.main()
