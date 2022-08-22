import unittest
import warnings
from dataclasses import astuple
from typing import Any

from npm_calmarendian_date.string_conversions import DateString
from npm_calmarendian_date.exceptions import CalmarendianDateError, CalmarendianDateFormatError


class VeryBasicTests(unittest.TestCase):
    def test_basic_attribute_assignment(self):
        data = [
            ("777-7-07-7", ("777-7-07-7", "777-7-07-7")),
            ("777-1-23-4  ", ("777-1-23-4  ", "777-1-23-4")),
            (" - 777-1-23-4", (" - 777-1-23-4", "777-1-23-4")),
            (" - 777-1-23-4--", (" - 777-1-23-4--", "777-1-23-4")),
        ]
        for line_item in data:
            test_item, expected = line_item
            with self.subTest(i=test_item):
                ds = DateString(test_item)
                self.assertTupleEqual(expected, (ds.original_string, ds.raw_data))


class UtilityTests(unittest.TestCase):
    def test_era_consistency(self):
        data = [
            ((50, "CE"), "DATE STRING: Cycle 50 is not in Current Era"),
            ((500, "CE"), "DATE STRING: Cycle 500 is not in Current Era"),
            ((501, "CE"), ""),
            ((500, "BH"), ""),
            ((501, "BH"), "DATE STRING: Cycle 501 is not Before History"),
            ((0, "BZ"), ""),
            ((0, "BH"), "DATE STRING: Cycle 0 Era is BZ, not BH"),
            ((0, "CE"), "DATE STRING: Cycle 0 is not in Current Era"),
        ]
        for index, item in enumerate(data):
            test_item, expected = item
            with self.subTest(i=index):
                with warnings.catch_warnings(record=True) as w:
                    DateString.check_era_consistency(*test_item)
                    if expected:
                        self.assertEqual(len(w), 1)
                        self.assertIs(w[0].category, UserWarning)
                        self.assertEqual(expected, w[0].message.__str__())
                    else:
                        self.assertEqual(len(w), 0, msg="No warning was expected.")

    def test_split_day_in_season(self):
        data = [
            # Valid day-in-season numbers
            (1, (1, 1)),
            (350, (50, 7)),
            (255, (37, 3)),
            (355, (51, 5)),
            (358, (51, 8)),
            # Garbage in, garbage out
            (0, (0, 7)),
            (360, (51, 10)),
            (1360, (51, 1010)),
        ]
        for item in data:
            test_item, expected = item
            with self.subTest(i=item):
                self.assertEqual(expected, DateString.split_day_in_season(test_item))


class GeneralBadDataTests(unittest.TestCase):
    def test_real_garbage_inputs(self):
        data = [
            ("garbage", "DATE STRING: 'garbage' is not a valid date string."),
            (7, "DATE STRING must be 'str', not 'int'."),
            (["777-7-07-7"], "DATE STRING must be 'str', not 'list'."),
            ("", "DATE STRING '' is devoid of useful data."),
            (" -- ", "DATE STRING ' -- ' is devoid of useful data."),
        ]
        for line_item in data:
            test_item, expected = line_item
            with self.subTest(i=test_item):
                with self.assertRaises(CalmarendianDateFormatError) as cm:
                    DateString(test_item)
                self.assertEqual(expected, cm.exception.__str__())


class GCNConversionTests(unittest.TestCase):
    def test_bad_formats(self):
        # Missing day element:
        with self.assertRaises(CalmarendianDateError):
            DateString('02-077-7-07')
        # Single digit Grand Cycle number:
        with self.assertRaises((CalmarendianDateError, CalmarendianDateFormatError)):
            DateString('2-077-7-07-7')
        # Out of domain cycle-in-grand-cycle:
        with self.assertRaises(CalmarendianDateFormatError):
            DateString('02-877-7-07-7')
        # Out of domain season:
        with self.assertRaisesRegex(CalmarendianDateFormatError, f"DATE STRING: '02-077-8-23-4'"):
            DateString('02-077-8-23-4')
        with self.assertRaisesRegex(CalmarendianDateError, "'list'"):
            arg: Any = []
            DateString(arg)

    def test_good_inputs(self):
        data = [
            {"date_string": '00-001-1-01-1', "result": (0, 1, 1, 1, 1)},
            {"date_string": '00-688-4-05-6', "result": (0, 688, 4, 5, 6)},
            {"date_string": '00-700-7-51-8', "result": (0, 700, 7, 51, 8)},
            {"date_string": '01-001-1-01-1', "result": (1, 1, 1, 1, 1)},
            {"date_string": '01-423-1-23-4', "result": (1, 423, 1, 23, 4)},
            {"date_string": '02-001-1-02-3', "result": (2, 1, 1, 2, 3)},
            {"date_string": '02-077-3-04-5', "result": (2, 77, 3, 4, 5)},
            {"date_string": '02-077-7-07-7', "result": (2, 77, 7, 7, 7)},
            {"date_string": '02-078-1-01-1', "result": (2, 78, 1, 1, 1)},
            {"date_string": '15-199-7-51-4', "result": (15, 199, 7, 51, 4)},
            {"date_string": '99-700-7-51-8', "result": (99, 700, 7, 51, 8)},
        ]
        for item in data:
            d = DateString(item["date_string"])
            self.assertTupleEqual(item["result"], astuple(d.dts)[:5])


class CSNConversionTests(unittest.TestCase):
    def test_bad_formats(self):
        data = [
            # Invalid season:
            ("777-8-07-2", "DATE STRING: '777-8-07-2' is not a valid date string."),
            # Two digit cycle number in an otherwise valid CSN string:
            ("77-7-07-7", "DATE STRING: '77-7-07-7' is not a valid date string."),
            # Invalid Era Marker
            ("100-1-23-4 AD", "DATE STRING: '100-1-23-4 AD' is not a valid date string."),
            # An out of domain week number
            ("100-1-63-4", "DATE STRING: '100-1-63-4' is not a valid date string."),
            # Whilst a four digit cycle number is not illegal, padding to four digits is:
            ("0777-1-23-4", "DATE STRING: '0777-1-23-4' is not a valid date string."),
        ]
        for line_item in data:
            test_item, expected = line_item
            with self.subTest(i=test_item):
                with self.assertRaises(CalmarendianDateFormatError) as cm:
                    DateString(test_item)
                self.assertEqual(expected, cm.exception.__str__())

    def test_dubious_era_markers(self):
        with self.assertWarns(UserWarning) as my_warning:
            d = DateString("400-1-23-4 CE")  # Cycle 400 is not in Current Era
        self.assertRegex(my_warning.warning.__str__(), "Current Era")
        self.assertTupleEqual((1, 400, 1, 23, 4), astuple(d.dts)[:5])  # A warning is issued but date calculated anyway

        with self.assertWarns(UserWarning) as my_warning:
            d = DateString("777-3-48-6 BH")  # Cycle 777 is not Before History
        self.assertRegex(my_warning.warning.__str__(), "Before History")
        self.assertTupleEqual((2, 77, 3, 48, 6), astuple(d.dts)[:5])  # A warning is issued but date calculated anyway

        with self.assertWarns(UserWarning) as my_warning:
            d = DateString("000-3-48-6 BH")  # Cycle 0 is not Before History
        self.assertRegex(my_warning.warning.__str__(), "BZ, not BH")
        self.assertTupleEqual((0, 700, 3, 48, 6), astuple(d.dts)[:5])  # A warning is issued but date calculated anyway

    def test_cycle_conversion(self):
        data = [
            {"date_string": '1401-1-23-4 bz', "result": (-2, 699)},
            {"date_string": '1400-1-23-4 bz', "result": (-2, 700)},
            {"date_string": '1399-1-23-4 BZ', "result": (-1, 1)},
            {"date_string": '701-1-23-4 BZ', "result": (-1, 699)},
            {"date_string": '700-1-23-4 BZ', "result": (-1, 700)},
            {"date_string": '699-1-23-4 BZ', "result": (0, 1)},
            {"date_string": '002-1-23-4 BZ', "result": (0, 698)},
            {"date_string": '001-1-23-4 BZ', "result": (0, 699)},
            {"date_string": '000-1-23-4 BZ', "result": (0, 700)},
            {"date_string": '000-1-23-4', "result": (0, 700)},
            {"date_string": '001-1-23-4', "result": (1, 1)},
            {"date_string": '002-1-23-4', "result": (1, 2)},
            {"date_string": '699-1-23-4', "result": (1, 699)},
            {"date_string": '700-1-23-4', "result": (1, 700)},
            {"date_string": '701-1-23-4', "result": (2, 1)},
            {"date_string": '777-1-23-4', "result": (2, 77)},
            {"date_string": '1399-1-23-4', "result": (2, 699)},
            {"date_string": '1400-1-23-4', "result": (2, 700)},
            {"date_string": '1401-1-23-4', "result": (3, 1)},
        ]
        for item in data:
            d = DateString(item["date_string"])
            self.assertTupleEqual(item["result"], (d.dts.grand_cycle, d.dts.cycle))

    def test_good_inputs(self):
        data = [
            {"date_string": '699-1-01-1 BZ', "result": (0, 1, 1, 1, 1)},
            {"date_string": '012-4-05-6 BZ', "result": (0, 688, 4, 5, 6)},
            {"date_string": '000-7-51-8 BZ', "result": (0, 700, 7, 51, 8)},
            {"date_string": '001-1-01-1 BH', "result": (1, 1, 1, 1, 1)},
            {"date_string": '423-1-23-4 BH', "result": (1, 423, 1, 23, 4)},
            {"date_string": '701-1-02-3 CE', "result": (2, 1, 1, 2, 3)},
            {"date_string": '777-3-04-5 CE', "result": (2, 77, 3, 4, 5)},
            {"date_string": '777-7-07-7 CE', "result": (2, 77, 7, 7, 7)},
            {"date_string": '778-1-01-1 CE', "result": (2, 78, 1, 1, 1)},
            {"date_string": '9999-7-51-4 CE', "result": (15, 199, 7, 51, 4)},
        ]
        for item in data:
            d = DateString(item["date_string"])
            self.assertTupleEqual(item["result"], astuple(d.dts)[:5])


class DSNConversionTests(unittest.TestCase):
    # TODO Separate the CalmarendianDate DATA_SET_ONE into a global resource that can be used here.
    # TODO Make some tests here
    # TODO Add tests at the CalmarendianDate level, too.
    pass


if __name__ == '__main__':
    unittest.main()
