import unittest

from npm_calmarendian_date import CalmarendianDate
from npm_calmarendian_date.c_date_config import CDateConfig
from npm_calmarendian_date.exceptions import CalmarendianDateError, CalmarendianDateDomainError


class ARTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = [
            {'apocalypse_reckoning': -3_624_849, 'adr': -1718100, 'csn': '699-1-01-1 BZ'},
            {'apocalypse_reckoning': -2117, 'adr': 1904632, 'csn': '776-7-51-1'},
            {'apocalypse_reckoning': -100, 'adr': 1906649, 'csn': '777-6-38-5'},
            {'apocalypse_reckoning': -10, 'adr': 1906739, 'csn': '777-7-01-4'},
            {'apocalypse_reckoning': -1, 'adr': 1906748, 'csn': '777-7-02-6'},
            {'apocalypse_reckoning': 0, 'adr': 1906749, 'csn': '777-7-02-7'},
            {'apocalypse_reckoning': 1, 'adr': 1906750, 'csn': '777-7-03-1'},
            {'apocalypse_reckoning': 10, 'adr': 1906759, 'csn': '777-7-04-3'},
            {'apocalypse_reckoning': 100, 'adr': 1906849, 'csn': '777-7-17-2'},
            {'apocalypse_reckoning': 343, 'adr': 1907092, 'csn': '777-7-51-7'},
            {'apocalypse_reckoning': 168_185_250, 'adr': 170091999, 'csn': '69300-7-51-8'},
        ]

    def test_ar_epoch(self):
        ar0 = CalmarendianDate(CDateConfig.APOCALYPSE_EPOCH_ADR)
        self.assertEqual(CalmarendianDate.from_date_string('777-7-02-7'), ar0)

    def test_ar_constructor(self):
        for item in self.data:
            with self.subTest(i=item['apocalypse_reckoning']):
                d: CalmarendianDate = CalmarendianDate.from_apocalypse_reckoning(item['apocalypse_reckoning'])
                self.assertEqual(item['adr'], d.adr)
                self.assertEqual(item['csn'], d.csn())

    def test_ar_constructor_with_duff_data(self):
        self.assertRaises(CalmarendianDateDomainError, CalmarendianDate.from_apocalypse_reckoning, -3_624_850)
        self.assertRaises(CalmarendianDateDomainError, CalmarendianDate.from_apocalypse_reckoning, 168_185_251)
        self.assertRaises(CalmarendianDateError, CalmarendianDate.from_apocalypse_reckoning, 'duff data')
        self.assertRaises(CalmarendianDateError, CalmarendianDate.from_apocalypse_reckoning, {})

    def test_ar_getter(self):
        for item in self.data:
            with self.subTest(i=item['apocalypse_reckoning']):
                d = CalmarendianDate(item['adr'])
                self.assertEqual(item['apocalypse_reckoning'], d.apocalypse_reckoning)

    def test_ar_setter(self):
        for item in self.data:
            with self.subTest(i=item['apocalypse_reckoning']):
                d = CalmarendianDate.from_date_string('777-7-07-7')
                d.apocalypse_reckoning = item['apocalypse_reckoning']
                self.assertEqual(item['apocalypse_reckoning'], d.apocalypse_reckoning)
                self.assertEqual(item['adr'], d.adr)

    def test_ar_setter_with_duff_data(self):
        with self.assertRaises(CalmarendianDateError):
            d = CalmarendianDate.from_date_string('777-7-07-7')
            d.apocalypse_reckoning(-3_624_850)
        with self.assertRaises(CalmarendianDateError):
            d = CalmarendianDate.from_date_string('777-7-07-7')
            d.apocalypse_reckoning(168_185_251)

    def test_today(self):
        d: CalmarendianDate = CalmarendianDate.today()
        self.assertEqual(1, d.apocalypse_reckoning)
        self.assertEqual('777-7-03-1', d.csn())


if __name__ == '__main__':
    unittest.main()
