import unittest
from collections import namedtuple
from dataclasses import astuple
from typing import Any

from npm_calmarendian_date import CalmarendianDate
from npm_calmarendian_date import CalmarendianTimeDelta
from npm_calmarendian_date.c_date_config import CDateConfig
from npm_calmarendian_date.c_date_utils import DateTimeStruct
from npm_calmarendian_date.calmarendian_date import EraMarker
from npm_calmarendian_date.date_elements import GrandCycle, CycleInGrandCycle, Season, Week, Day
from npm_calmarendian_date.exceptions import CalmarendianDateError
import global_data_sets as global_data


class BasicFunctionalityTests(unittest.TestCase):
    ResultSet = namedtuple('ResultSet', 'gc c s w d')

    def test_type_error(self):
        with self.assertRaises(CalmarendianDateError):
            s: Any = "Random String"
            CalmarendianDate(s)
        with self.assertRaisesRegex(CalmarendianDateError, "'tuple'"):
            s: Any = (23, 45)
            CalmarendianDate(s)

    def test_out_of_range(self):
        for item in global_data.c_date_out_of_range:
            with self.subTest(i=item.csn):
                with self.assertRaises(item.exc_type) as cm:
                    CalmarendianDate(item.adr)
                expected = f"ADR: {item.adr} is out of range."
                self.assertEqual(expected, cm.exception.__str__())

    def test_simple_adr_set(self):
        d = CalmarendianDate(1_234_567)
        self.assertEqual(1_234_567, d.adr)
        self.assertEqual('Wednesday, Week 50 of Onset 503', d.colloquial_date())
        d.adr = 1_234_568
        self.assertEqual(1_234_568, d.adr)
        self.assertEqual('Thursday, Week 50 of Onset 503', d.colloquial_date())

    def test_cycle_decode(self):
        items = [
            {"days": 2454, "cycle": 1},
            {"days": 2455, "cycle": 2},
            {"days": 14_724, "cycle": 6},
            {"days": 14_725, "cycle": 7},
            {"days": 17_181, "cycle": 7},
            {"days": 17_182, "cycle": 8},
            {"days": 861_505, "cycle": 352},
            {"days": 1_718_100, "cycle": 700},
        ]
        for item in items:
            self.assertEqual(item["cycle"], CalmarendianDate.cycle_decode(item["days"]))

    def test_basic_setting(self):
        data = [
            -5000,
            0,
            50000,
            CDateConfig.APOCALYPSE_EPOCH_ADR
        ]
        for item in data:
            with self.subTest(i=item):
                d = CalmarendianDate(item)
                self.assertEqual(item, d.adr)

    def test_elemental_adr_set(self):
        items = [
            {"input": -1_718_100, "result": self.ResultSet(0, 1, 1, 1, 1)},
            {"input": -30_825, "result": self.ResultSet(0, 688, 4, 5, 6)},
            {"input": 0, "result": self.ResultSet(0, 700, 7, 51, 8)},
            {"input": 1, "result": self.ResultSet(1, 1, 1, 1, 1)},
            {"input": 1_035_926, "result": self.ResultSet(1, 423, 1, 23, 4)},
            {"input": 1_905_361, "result": self.ResultSet(2, 77, 3, 4, 5)},
            {"input": 1_906_784, "result": self.ResultSet(2, 77, 7, 7, 7)},
            {"input": 1_907_093, "result": self.ResultSet(2, 78, 1, 1, 1)},
            {"input": 170_091_999, "result": self.ResultSet(99, 700, 7, 51, 8)},
        ]
        for item in items:
            with self.subTest(i=item["input"]):
                d = CalmarendianDate(item["input"])
                r = item["result"]
                self.assertEqual(r.gc, d.grand_cycle.number)
                self.assertEqual(r.c, d.cycle.number)
                self.assertEqual(r.s, d.season.number)
                self.assertEqual(r.w, d.week.number)
                self.assertEqual(r.d, d.day.number)

    def test_output_gcn(self):
        items = [
            {"input": CDateConfig.MIN_ADR, "result": "00-001-1-01-1"},
            {"input": -30_825, "result": "00-688-4-05-6"},
            {"input": 0, "result": "00-700-7-51-8"},
            {"input": 1, "result": "01-001-1-01-1"},
            {"input": 1_035_926, "result": "01-423-1-23-4"},
            {"input": 1_718_111, "result": "02-001-1-02-3"},
            {"input": 1_905_361, "result": "02-077-3-04-5"},
            {"input": 1_906_784, "result": "02-077-7-07-7"},
            {"input": CDateConfig.APOCALYPSE_EPOCH_ADR, "result": "02-077-7-02-7"},
            {"input": CDateConfig.MAX_ADR, "result": "99-700-7-51-8"},
        ]
        for item in items:
            # Test adr -> gcn -> adr
            d = CalmarendianDate(item["input"])
            self.assertEqual(item["result"], d.grand_cycle_notation())
            self.assertEqual(item["result"], d.gcn())
            dx = CalmarendianDate.from_date_string(d.gcn())
            self.assertEqual(d.adr, dx.adr)

            # Test gcn -> adr -> gcn
            dy = CalmarendianDate.from_date_string(item["result"])
            self.assertEqual(item["input"], dy.adr)
            dz = CalmarendianDate(dy.adr)
            self.assertEqual(dy.gcn(), dz.gcn())

    def test_abs_cycle_ref(self):
        for item in global_data.c_date_data:
            with self.subTest(i=item.csn):
                d = CalmarendianDate(item.adr)
                self.assertTupleEqual((item.acr, item.era_marker), d.absolute_cycle_ref())

    def test_abs_season_ref(self):
        for item in global_data.c_date_data:
            with self.subTest(i=item.csn):
                d = CalmarendianDate(item.adr)
                self.assertEqual(item.asr, d.absolute_season_ref())

    def test_output_csn(self):
        for item in global_data.c_date_data:
            with self.subTest(adr=item.adr):
                # Test adr -> csn -> adr
                d = CalmarendianDate(item.adr)
                self.assertEqual(item.csn, d.common_symbolic_notation())
                self.assertEqual(item.csn, d.csn())
                dx = CalmarendianDate.from_date_string(d.csn())
                self.assertEqual(d.adr, dx.adr)

                # Test csn -> adr -> csn
                dy = CalmarendianDate.from_date_string(item.csn)
                self.assertEqual(item.adr, dy.adr)
                dz = CalmarendianDate(dy.adr)
                self.assertEqual(dy.csn(), dz.csn())

    def test_csn_era_variants(self):
        d = CalmarendianDate(-30_825)
        self.assertEqual("012-4-05-6 BZ", d.common_symbolic_notation())
        self.assertEqual("012-4-05-6 BZ", d.common_symbolic_notation(era_marker="BH"))
        self.assertEqual("012-4-05-6 BZ", d.common_symbolic_notation(era_marker="CE"))
        d = CalmarendianDate(1_035_926)
        self.assertEqual("423-1-23-4", d.common_symbolic_notation())
        self.assertEqual("423-1-23-4 BH", d.common_symbolic_notation(era_marker="BH"))
        self.assertEqual("423-1-23-4 BH", d.common_symbolic_notation(era_marker="CE"))
        d = CalmarendianDate(1_905_361)
        self.assertEqual("777-3-04-5", d.common_symbolic_notation())
        self.assertEqual("777-3-04-5", d.common_symbolic_notation(era_marker="BH"))
        self.assertEqual("777-3-04-5 CE", d.common_symbolic_notation(era_marker="ce"))

    def test_resolution(self):
        self.assertIsInstance(CalmarendianDate.resolution, CalmarendianTimeDelta)
        self.assertTupleEqual((1, 0, 0), CalmarendianDate.resolution._get_state())
        self.assertEqual("+1 day + 00:00:00", str(CalmarendianDate.resolution))

    def test_to_date_time_struct(self):
        for index, item in enumerate(global_data.c_date_data):
            dx = CalmarendianDate(item.adr)
            with self.subTest(i=index):
                self.assertTupleEqual(item.base_elements, astuple(dx.to_date_time_struct()))


class SecondaryConstructorsTests(unittest.TestCase):
    def test_new_from_objects(self):
        for index, item in enumerate(global_data.c_date_data):
            gc = GrandCycle(item.base_elements[0])
            c = CycleInGrandCycle(item.base_elements[1])
            s = Season(item.base_elements[2])
            w = Week(item.base_elements[3], s)
            d = Day(item.base_elements[4], w, c)
            dx = CalmarendianDate.from_objects(gc, c, s, w, d)
            with self.subTest(i=index):
                self.assertEqual(item.adr, dx.adr)
                self.assertEqual(item.gcn, dx.gcn())

    def test_create_from_numbers(self):
        data = [
            {"input": (1, 423, 1, 23, 4),
             "result": {
                 "gcn": "01-423-1-23-4",
                 "adr": 1_035_926
             }},
            {"input": (2, 1, 1, 2, 3),
             "result": {
                 "gcn": "02-001-1-02-3",
                 "adr": 1_718_111
             }},
        ]
        for item in data:
            d = CalmarendianDate.from_numbers(*item["input"])
            self.assertEqual(item["result"]["gcn"], d.gcn())
            self.assertEqual(item["result"]["adr"], d.adr)

    def test_create_from_gcn(self):
        data = [
            {"date_string": '00-001-1-01-1', "result": CDateConfig.MIN_ADR},
            {"date_string": '00-688-4-05-6', "result": -30_825},
            {"date_string": '00-700-7-51-8', "result": 0},
            {"date_string": '01-001-1-01-1', "result": 1},
            {"date_string": '01-423-1-23-4', "result": 1_035_926},
            {"date_string": '02-001-1-02-3', "result": 1_718_111},
            {"date_string": '02-077-3-04-5', "result": 1_905_361},
            {"date_string": '02-077-7-07-7', "result": 1_906_784},
            {"date_string": '02-077-7-02-7', "result": CDateConfig.APOCALYPSE_EPOCH_ADR},
            {"date_string": '15-199-7-51-4', "result": 24_541_844},
            {"date_string": '99-700-7-51-8', "result": CDateConfig.MAX_ADR},
        ]
        for item in data:
            d = CalmarendianDate.from_date_string(item["date_string"])
            self.assertEqual(item["result"], d.adr)

    def test_create_from_csn(self):
        data = [
            {"date_string": '699-1-01-1 BZ', "result": CDateConfig.MIN_ADR},
            {"date_string": '012-4-05-6 BZ', "result": -30_825},
            {"date_string": '000-7-51-8 BZ', "result": 0},
            {"date_string": '001-1-01-1', "result": 1},
            {"date_string": '423-1-23-4', "result": 1_035_926},
            {"date_string": '701-1-02-3', "result": 1_718_111},
            {"date_string": '777-3-04-5', "result": 1_905_361},
            {"date_string": '777-7-07-7', "result": 1_906_784},
            {"date_string": '777-7-02-7', "result": CDateConfig.APOCALYPSE_EPOCH_ADR},
            {"date_string": '9999-7-51-4', "result": 24_541_844},
        ]
        for item in data:
            d = CalmarendianDate.from_date_string(item["date_string"])
            self.assertEqual(item["result"], d.adr)

    def test_from_time_date_struct(self):
        for item in global_data.c_date_data:
            dts = DateTimeStruct(*item.base_elements)
            d0 = CalmarendianDate.from_date_time_struct(dts)
            d1 = CalmarendianDate(item.adr)
            d2 = CalmarendianDate.from_date_time_struct(d1.to_date_time_struct())
            expected = item.adr
            with self.subTest(i=item.csn):
                # test dts -> CalDate -> dts
                self.assertEqual(expected, d0.adr)
                self.assertEqual(d0, d1)
                self.assertEqual(dts, d0.to_date_time_struct())
                # test CalDate -< dts -> CalDAte
                self.assertEqual(dts, d1.to_date_time_struct())
                self.assertEqual(d1, d2)
                self.assertEqual(expected, d2.adr)

    def test_from_bad_date_time_struct(self):
        data = [
            (2, 77, 7, 2, 7, 0, 0, 0, 0, 0),
            "junk"
        ]
        for index, item in enumerate(data):
            with self.subTest(i=index):
                with self.assertRaises(CalmarendianDateError):
                    # noinspection PyTypeChecker
                    CalmarendianDate.from_date_time_struct(item)

    def test_from_dsn_string(self):
        # TODO test_from_dsn_string
        pass

    def test_dsn_adr_dsn(self):
        # TODO test dsn -> adr -> dsn there and back again
        pass

    def test_adr_dsn_adr(self):
        # TODO test adr -> dsn -> adr there and back again
        pass

    def test_from_bad_dsn_string(self):
        # TODO test_from_bad_dsn_string
        pass

    def test_from_bad_dsn_day(self):
        for item in global_data.dsn_bad_days:
            test_item_0 = DateTimeStruct(*item.base_elements)
            test_item_1 = item.dsn
            expected_exc_type = item.exc_type
            with self.subTest(i=item.dsn):
                with self.assertRaises(expected_exc_type) as cm_0:
                    CalmarendianDate.from_date_time_struct(test_item_0)
                self.assertEqual(item.exc_msg, cm_0.exception.__str__())
                with self.assertRaises(expected_exc_type) as cm_1:
                    CalmarendianDate.from_date_string(test_item_1)
                self.assertEqual(item.exc_msg, cm_1.exception.__str__())


class ColloquialDateTests(unittest.TestCase):
    @staticmethod
    def c_day(offset: int) -> Day:
        return CalmarendianDate(1_889_897 + offset).day

    def test_day_of_the_week_names(self):
        d = self.c_day(7)
        self.assertEqual("Sunday", d.name())
        self.assertEqual("Sun", d.short_name())
        d = self.c_day(12)
        self.assertEqual("\u03A9.5", d.short_name())
        self.assertEqual("Festival Five", d.name())

    def test_short_day_names_default(self):
        day_names = [self.c_day(x).short_name() for x in range(1, 8)]
        self.assertSequenceEqual(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], day_names)

    def test_short_day_names_too_long(self):
        # If a chars value greater than 3 given, default to three
        day_names = [self.c_day(x).short_name(chars=6) for x in range(1, 8)]
        self.assertSequenceEqual(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], day_names)

    def test_short_day_names_short(self):
        day_names = [self.c_day(x).short_name(chars=3) for x in range(1, 8)]
        self.assertSequenceEqual(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], day_names)

    def test_short_day_names_shorter(self):
        day_names = [self.c_day(x).short_name(chars=2) for x in range(1, 8)]
        self.assertSequenceEqual(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"], day_names)

    def test_short_day_names_shortest(self):
        day_names = [self.c_day(x).short_name(chars=1) for x in range(1, 8)]
        self.assertSequenceEqual(["M", "T", "W", "Th", "F", "S", "Su"], day_names)

    def test_short_day_names_too_short(self):
        # If a chars value less than one given, default to 1
        day_names = [self.c_day(x).short_name(chars=0) for x in range(1, 8)]
        self.assertSequenceEqual(["M", "T", "W", "Th", "F", "S", "Su"], day_names)

    def test_short_day_festival(self):
        self.assertEqual("\u03A9.1", self.c_day(8).short_name())
        self.assertEqual("\u03A9.2", self.c_day(9).short_name(chars=3))
        self.assertEqual("\u03A93", self.c_day(10).short_name(chars=2))
        self.assertEqual("\u03A97", self.c_day(14).short_name(chars=1))

    def test_month_names(self):
        data = [
            (1, "Midwinter"),
            (2, "Thaw"),
            (3, "Spring"),
            (4, "Perihelion"),
            (5, "High Summer"),
            (6, "Autumn"),
            (7, "Onset")
        ]
        for i in data:
            s = Season(i[0])
            with self.subTest(i=i):
                self.assertEqual(i[1], s.name())

    def test_colloquial_standard(self):
        d = CalmarendianDate(-1_230_683)
        self.assertEqual("Sunday, Week 6 of High Summer 501 BZ", d.colloquial_date())
        self.assertEqual("Sunday, Week 6 of High Summer 501 BZ", d.colloquial_date(era_marker="BH"))
        self.assertEqual("Sunday, Week 6 of High Summer 501 BZ", d.colloquial_date(era_marker="ce"))
        d = CalmarendianDate(543_511)
        self.assertEqual("Saturday, Week 5 of Perihelion 222", d.colloquial_date())
        self.assertEqual("Saturday, Week 5 of Perihelion 222 BH", d.colloquial_date(era_marker="BH"))
        self.assertEqual("Saturday, Week 5 of Perihelion 222 BH", d.colloquial_date(era_marker="CE"))
        d = CalmarendianDate(1_907_242)
        self.assertEqual("Wednesday, Week 22 of Midwinter 778", d.colloquial_date())
        self.assertEqual("Wednesday, Week 22 of Midwinter 778", d.colloquial_date(era_marker="BH"))
        self.assertEqual("Wednesday, Week 22 of Midwinter 778 CE", d.colloquial_date(era_marker="CE"))

    def test_colloquial_festival(self):
        d = CalmarendianDate(-171_812)
        self.assertEqual("Festival 6 of 70 BZ", d.colloquial_date())
        self.assertEqual("Festival 6 of 70 BZ", d.colloquial_date(era_marker="BH"))
        self.assertEqual("Festival 6 of 70 BZ", d.colloquial_date(era_marker="CE"))
        d = CalmarendianDate(1_200_210)
        self.assertEqual("Festival 1 of 489", d.colloquial_date())
        self.assertEqual("Festival 1 of 489 BH", d.colloquial_date(era_marker="BH"))
        self.assertEqual("Festival 1 of 489 BH", d.colloquial_date(era_marker="CE"))
        d = CalmarendianDate.from_numbers(2, 77, 7, 51, 7)
        self.assertEqual("Festival 7 of 777", d.colloquial_date())
        self.assertEqual("Festival 7 of 777", d.colloquial_date(era_marker="BH"))
        self.assertEqual("Festival 7 of 777 CE", d.colloquial_date(era_marker="CE"))

    def test_colloquial_standard_verbose(self):
        d = CalmarendianDate(-1_559_813)
        self.assertEqual("Monday of Week 23 of Perihelion 635 Before Time Zero",
                         d.colloquial_date(verbose=True))
        self.assertEqual("Monday of Week 23 of Perihelion 635 Before Time Zero",
                         d.colloquial_date(era_marker="BH", verbose=True))
        self.assertEqual("Monday of Week 23 of Perihelion 635 Before Time Zero",
                         d.colloquial_date(era_marker="CE", verbose=True))
        d = CalmarendianDate(3)
        self.assertEqual("Wednesday of Week 1 of Midwinter 1",
                         d.colloquial_date(verbose=True))
        self.assertEqual("Wednesday of Week 1 of Midwinter 1 Before History",
                         d.colloquial_date(era_marker="BH", verbose=True))
        self.assertEqual("Wednesday of Week 1 of Midwinter 1 Before History",
                         d.colloquial_date(era_marker="CE", verbose=True))
        d = CalmarendianDate(1_484_537)
        self.assertEqual("Friday of Week 45 of Autumn 605",
                         d.colloquial_date(verbose=True))
        self.assertEqual("Friday of Week 45 of Autumn 605",
                         d.colloquial_date(era_marker="BH", verbose=True))
        self.assertEqual("Friday of Week 45 of Autumn 605 Current Era",
                         d.colloquial_date(era_marker="CE", verbose=True))

    def test_colloquial_festival_verbose(self):
        d = CalmarendianDate(-323_986)
        self.assertEqual("Festival Four of 132 Before Time Zero", d.colloquial_date(verbose=True))
        self.assertEqual("Festival Four of 132 Before Time Zero", d.colloquial_date(era_marker="BH", verbose=True))
        self.assertEqual("Festival Four of 132 Before Time Zero", d.colloquial_date(era_marker="CE", verbose=True))
        d = CalmarendianDate(1_048_041)
        self.assertEqual("Festival Seven of 427", d.colloquial_date(verbose=True))
        self.assertEqual("Festival Seven of 427 Before History", d.colloquial_date(era_marker="BH", verbose=True))
        self.assertEqual("Festival Seven of 427 Before History", d.colloquial_date(era_marker="CE", verbose=True))
        d = CalmarendianDate(1_718_101)
        self.assertEqual("Festival Eight of 700", d.colloquial_date(verbose=True))
        self.assertEqual("Festival Eight of 700", d.colloquial_date(era_marker="BH", verbose=True))
        self.assertEqual("Festival Eight of 700 Current Era", d.colloquial_date(era_marker="CE", verbose=True))

    def test_str_and_repr(self):
        data = [
            {"input": CDateConfig.MIN_ADR, "result": "699-1-01-1 BZ"},
            {"input": -30_825, "result": "012-4-05-6 BZ"},
            {"input": 0, "result": "000-7-51-8 BZ"},
            {"input": 1, "result": "001-1-01-1"},
            {"input": 1_035_933, "result": "423-1-24-4"},
            {"input": 1_718_111, "result": "701-1-02-3"},
            {"input": 1_905_361, "result": "777-3-04-5"},
            {"input": 1_906_784, "result": "777-7-07-7"},
            {"input": CDateConfig.APOCALYPSE_EPOCH_ADR, "result": "777-7-02-7"},
            {"input": 24_541_844, "result": "9999-7-51-4"},
        ]
        for item in data:
            with self.subTest(i=item["input"]):
                d = CalmarendianDate(item["input"])
                self.assertEqual(item["result"], str(d))
                self.assertEqual(f"CalmarendianDate({d.adr})", repr(d))
                dx = eval(repr(d))
                self.assertTrue(d == dx)
                self.assertFalse(d is dx)


class WeekNameTests(unittest.TestCase):
    def test_week_names(self):
        data = [
            {"date": "774-7-14-7", "result": "Daisy"},
            {"date": "775-5-50-1", "result": "Heliotrope"},
            {"date": "776-7-51-4", "result": "Festival"},
        ]
        for item in data:
            with self.subTest(i=item["date"]):
                d = CalmarendianDate.from_date_string(item["date"])
                self.assertEqual(item["result"], d.week.name())


class WeekendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = [
            {'date': '707-1-01-6', "results": ('Short', 2.0)},
            {'date': '778-7-05-5', "results": ('Long', 3.0)},
            {'date': '779-2-25-4', "results": ('Mid-Season', 3.5)},
            {'date': '780-3-50-3', "results": ('Heliotrope', 3.5)},
            {'date': '781-7-50-2', "results": ('Festival', 3.5)},
            {'date': '784-7-51-1', "results": ('', 0.0)},
        ]

    def test_weekend_data(self):
        for item in self.data:
            d = CalmarendianDate.from_date_string(item['date'])
            week_ident = f'S{d.week.season.number} W{d.week.number}'
            with self.subTest(i=week_ident):
                self.assertEqual(item['results'][0], d.week.weekend.descriptor)
                self.assertEqual(item['results'][1], d.week.weekend.duration)


if __name__ == '__main__':
    unittest.main()
