import unittest
import re

from npm_calmarendian_date.c_date_config import CDateConfig


class RegExTests(unittest.TestCase):
    def test_good_dsn_strings(self):
        data = [
            ("1 Onset 777", ("1", "Onset", "777", None)),
            ("12 Onset 777", ("12", "Onset", "777", None)),
            ("123 Onset 777", ("123", "Onset", "777", None)),
            ("123 Onset 12777", ("123", "Onset", "12777", None)),
            ("123 7 777", ("123", "7", "777", None)),
            ("09 Midwinter 777CE", ("09", "Midwinter", "777", "CE")),
            ("123 thaw 777 ce", ("123", "thaw", "777", "ce")),
            ("234 High Summer 888", ("234", "High Summer", "888", None)),
            ("123 h 776", ("123", "h", "776", None)),
            ("99-h-776", ("99", "h", "776", None)),
            ("123 Onset 777  CE", ("123", "Onset", "777", "CE")),
            ("123 -- Onset - - 777", ("123", "Onset", "777", None)),
        ]
        for item in data:
            test_item, expected = item
            with self.subTest(i=test_item):
                m = re.match(CDateConfig.DSN_DATE_STRING_RE, test_item)
                self.assertTrue(m, msg="RegEx match failed.")
                self.assertTupleEqual(expected, m.groups())

    def test_bad_dsn_strings(self):
        data = [
            "Onset 777",
            "123 hi776",
            "123 Onset 777 ad",
            "0123 Onset 777",
            "123 Onset 777 CE garbage",
            "123 777",
            "123 8 777",
            "123 11 777",
            "123 Onset 123777",
            "123 Mid-winter 678"
        ]
        for item in data:
            with self.subTest(i=item):
                self.assertFalse(re.match(CDateConfig.DSN_DATE_STRING_RE, item))


if __name__ == '__main__':
    unittest.main()
