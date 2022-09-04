import unittest
import warnings
from dataclasses import astuple

from npm_calmarendian_date import (
    split_float,
    round_half_away_from_zero
)
from npm_calmarendian_date.c_date_utils import DateTimeStruct, AbsoluteCycleRef, EraMarker
import tests.global_data_sets as global_data
from npm_calmarendian_date.date_elements import GrandCycle, CycleInGrandCycle


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
            # Any or all of the time elements can be omitted:
            (DateTimeStruct(2, 34, 5, 6, 7), (2, 34, 5, 6, 7, 0, 0, 0, 0, 0)),
            (DateTimeStruct(2, 34, 5, 6, 7, second=32), (2, 34, 5, 6, 7, 0, 0, 32, 0, 0)),
            # Should work with junk values - no data validation is performed:
            (DateTimeStruct(2, 34, 5, 6, 17), (2, 34, 5, 6, 17, 0, 0, 0, 0, 0)),
        ]
        for index, item in enumerate(data):
            test_item, expected = item
            with self.subTest(i=index):
                self.assertTupleEqual(expected, astuple(test_item))


class EraMarkerTests(unittest.TestCase):
    def test_ordering(self):
        a = EraMarker.BZ
        b = EraMarker.BH
        c = EraMarker.CE
        d = EraMarker.CE
        self.assertTrue(c == d)
        self.assertTrue(a < b < c)
        self.assertTrue(a <= b <= c)
        self.assertTrue(c > b > a)
        self.assertTrue(c >= b >= a)
        self.assertTrue(c != b and c != b and b != a)

    def test_type_mismatch(self):
        a = EraMarker.BZ
        self.assertRaises(TypeError, a == "BZ")

    def test_show_as_required(self):
        data = ["BZ", "", "", "BZ", "BH", "", "BZ", "BH", "CE"]
        era_list = [EraMarker.BZ, EraMarker.BH, EraMarker.CE]
        index = 0

        for level in era_list:
            for era_marker in era_list:
                test_result = "" if level < era_marker else era_marker.name
                with self.subTest(i=index):
                    self.assertEqual(data[index], test_result)
                index += 1


class AbsoluteCycleRefTest(unittest.TestCase):
    def test_default_constructor(self):
        for item in global_data.c_date_data:
            grand_cycle = GrandCycle(item.base_elements[0])
            cycle_in_grand_cycle = CycleInGrandCycle(item.base_elements[1])
            acr = AbsoluteCycleRef(grand_cycle, cycle_in_grand_cycle)
            with self.subTest(i=item.csn):
                self.assertEqual(item.acr, acr.cycle)
                self.assertEqual(item.era_marker, acr.era_marker)
                self.assertEqual(item.base_elements[:2], acr.normalized_gc_cgc())

    def test_from_raw_data(self):
        for item in global_data.c_date_data:
            cycle = item.acr
            era_marker = item.era_marker.name
            acr = AbsoluteCycleRef.from_cycle_era(cycle, era_marker)
            with self.subTest(i=item.csn):
                self.assertEqual(item.acr, acr.cycle)
                self.assertEqual(item.era_marker, acr.era_marker)
                self.assertEqual(item.base_elements[:2], acr.normalized_gc_cgc())

    def test_era_consistency_ll(self):
        for item in global_data.era_consistency_data:
            with self.subTest(i=item.csn):
                with warnings.catch_warnings(record=True) as w:
                    AbsoluteCycleRef.from_cycle_era(*item.cycle_era_pair)
                    if item.warn_msg:
                        self.assertEqual(len(w), 1, msg="Warning expected, none raised.")
                        self.assertIs(w[0].category, UserWarning)
                        self.assertEqual(item.warn_msg, w[0].message.__str__())
                    else:
                        self.assertEqual(len(w), 0, msg="Warning raised, none expected")


if __name__ == '__main__':
    unittest.main()
