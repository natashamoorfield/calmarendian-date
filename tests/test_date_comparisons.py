import unittest

from npm_calmarendian_date.calmarendian_date import CalmarendianDate


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.today = CalmarendianDate(1_906_904)  # 777-7-25-1
        cls.yesterday = CalmarendianDate(1_906_903)
        cls.tomorrow = CalmarendianDate(1_906_905)
        cls.election_day = CalmarendianDate.from_date_string('777-7-25-1')

    def test_equality(self):
        self.assertEqual(self.today, self.election_day)
        self.assertNotEqual(self.today, self.yesterday)
        self.assertTrue(self.today == self.election_day)
        self.assertFalse(self.yesterday == self.today)

    def test_lt(self):
        self.assertTrue(self.yesterday < self.tomorrow)
        self.assertFalse(self.today < self.yesterday)
        self.assertFalse(self.today < self.election_day)

    def test_le(self):
        self.assertTrue(self.yesterday <= self.today)
        self.assertTrue(self.today <= self.election_day)
        self.assertFalse(self.today <= self.yesterday)

    def test_gt(self):
        self.assertTrue(self.today > self.yesterday)
        self.assertFalse(self.today > self.tomorrow)
        self.assertFalse(self.today > self.election_day)

    def test_ge(self):
        self.assertTrue(self.today >= self.yesterday)
        self.assertTrue(self.today >= self.election_day)
        self.assertFalse(self.today >= self.tomorrow)


if __name__ == '__main__':
    unittest.main()
