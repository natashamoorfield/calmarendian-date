from typing import List

from npm_calmarendian_date.exceptions import CalmarendianDateError
from npm_calmarendian_date.c_date_config import CDateConfig
from math import floor
# from npm_calmarendian_date.date import CalmarendianDate


class GrandCycle(object):
    def __init__(self, grand_cycle: int):
        self.number = self.verified_grand_cycle_number(grand_cycle)

    @staticmethod
    def verified_grand_cycle_number(grand_cycle: int) -> int:
        """
        Return the grand_cycle number unaltered if it is valid, raise an exception otherwise.
        :param grand_cycle: The CalmarendianDate class should work, within reason,
        for any integer values of grand_cycle but there are other constraints to consider.
        Firstly, the estimated life of the star, Cal A, is only 470,000 grand cycles.
        Secondly, meaningful dates relating to human events and history fall only within Grand Cycles 1 and 2.
        On balance, we have decided to restrict grand_cycle numbers to between 0 and +99 inclusive.
        :return: A valid grand_cycle number.
        """
        if 0 <= grand_cycle <= 99:
            return grand_cycle
        error_message = " ".join([
            f"GRAND CYCLE: {grand_cycle} is an invalid input.",
            "Must be between 0 and 99 inclusive."
        ])
        raise CalmarendianDateError(error_message)

    def days_prior(self):
        """
        Return the number of days in Grand Cycles prior to the current one, relative to Time Zero.
        This will yield a negative number for Grand Cycle Zero.
        """
        return (self.number - 1) * CDateConfig.DAYS_per_GRAND_CYCLE

    def seasons_prior(self):
        """
        Return the number of seasons in the Grand Cycle prior to the current one, relative to Time Zero.
        this will yield a negative number for Grand Cycle Zero.
        """
        return (self.number - 1) * 4900


class CycleInGrandCycle(object):
    def __init__(self, cycle: int):
        self.number = self.verified_cycle_in_grand_cycle_number(cycle)

    @staticmethod
    def verified_cycle_in_grand_cycle_number(cycle: int) -> int:
        """
        Return the cycle_in_grand_cycle number unaltered if it is valid; raise an exception otherwise.
        :param cycle: Because, internally, we us "Grand Cycle" date notation,
        the cycle_in_grand_cycle value must lie between 1 and 700 (inc) in all circumstances.
        :return: A valid cycle_in_grand_cycle number.
        """
        if 1 <= cycle <= 700:
            return cycle
        error_message = " ".join([
            f"CYCLE in GRAND CYCLE: {cycle} is an invalid input.",
            "Must be between 1 and 700 inc."
        ])
        raise CalmarendianDateError(error_message)

    def festival_days(self):
        """
        Return the number of days in this cycle's festival.
        :return: 4 if the cycle number is not divisible by seven;
        8 if the cycle number is divisible by 700, otherwise 7
        """
        if self.number % 7 != 0:
            return 4
        if self.number % 700 == 0:
            return 8
        # Reach here if c is congruent to zero mod 7 but not zero mod 700.
        return 7

    def days_prior(self) -> int:
        """
        Return the number of days that have elapsed during the current grand-cycle
        prior to the start of the current cycle.
        Every cycle has (at least) 2454 days: 7 * 350 days for the seasons,
        plus four festival days; every seventh cycle has an extra three festival days.
        The eighth festival day every seven-hundredth cycle is accounted for in CDateConfig.DAYS_per_GRAND_CYCLE
        :return: Days elapsed in grand-cycle prior to the current cycle.
        """
        cycles_prior = self.number - 1
        return cycles_prior * 2454 + floor(cycles_prior / 7) * 3

    def seasons_prior(self) -> int:
        """
        Return the number of seasons that have elapsed during the current grand-cycle
        prior to the start of the current cycle.
        """
        return (self.number - 1) * 7


class Season(object):
    SEASON_NAMES: List[str] = [
        "Winter", "Thaw", "Spring", "Perihelion", "High Summer", "Autumn", "Onset"
    ]

    def __init__(self, season: int):
        self.number = self.verified_season(season)

    @staticmethod
    def verified_season(season: int) -> int:
        """
        Return the season number unaltered if it is valid; raise an exception otherwise.
        :param season: The season number must be between 1 and 7 (inc) in all circumstances.
        :return: A valid season number.
        """
        if not 1 <= season <= 7:
            error_message = " ".join([
                f"SEASON: {season} is an invalid input.",
                "Must be between 1 and 7 inc."
            ])
            raise CalmarendianDateError(error_message)
        return season

    def max_weeks(self) -> int:
        """
        Return the number of weeks in the season.
        :return: 51 for season 7, 60 otherwise
        """
        return 51 if self.number == 7 else 50

    def days_prior(self) -> int:
        """
        Return the number of days that have elapsed in the current cycle prior to the beginning of the current season.
        :return: Days prior to the current season.
        """
        return (self.number - 1) * 350

    def name(self) -> str:
        """
        Return the name of the season.
        """
        return self.SEASON_NAMES[self.number - 1]


class Week(object):
    def __init__(self, week: int, season: Season):
        self.number = self.verified_week(week, season)

    @staticmethod
    def verified_week(week: int, season: Season) -> int:
        """
        Return the week number unaltered, if it is valid; raise an exception otherwise.
        :param week: Ordinarily, the week number must be between 1 and 50 (inc).
        In season 7, 51 (Festival) is also valid.
        :param season: 7 indicates the season of Onset which has 51 weeks;
        any other valid value represents an ordinary 50-week season.
        :return: A valid week number.
        """
        mw = season.max_weeks()
        if not 1 <= week <= mw:
            error_message = " ".join([
                f"WEEK: {week} is not valid for season {season.number}.",
                f"Must be between 1 and {mw} inc."
            ])
            raise CalmarendianDateError(error_message)
        return week

    def days_prior(self):
        """
        Return the number of days that have elapsed in the current season prior to be beginning of the current week.
        :return: Days prior to the current week.
        """
        return (self.number - 1) * 7


class Day(object):
    DAY_NAMES: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    LONG_NUMBERS: List[str] = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"]

    def __init__(self, day: int, week: Week, cycle: CycleInGrandCycle):
        self.number = self.verified_day_number(day, week, cycle)
        self.festival = (week.number == 51)

    @staticmethod
    def verified_day_number(day: int, week: Week, cycle: CycleInGrandCycle) -> int:
        """
        Return the specified day number unaltered, if it is valid; raise an Exception otherwise.
        :param day: Ordinarily, the day number must be between 1 and 7 inclusive.
        In week 51 (Festival) the valid range is determined by the number of Festival days in the given cycle.
        :param week: Week number 51 indicates Festival, any other value represents an ordinary seven-day week.
        We are assuming the week number has already been verified.
        :param cycle: In week 51 the maximum value of 'day' is dependent upon cycle_in_grand_cycle.
        We are assuming the cycle_in_grand_cycle number has already been verified.
        :return: A valid day number.
        """
        max_days = cycle.festival_days() if week.number == 51 else 7
        if day <= 0 or day > max_days:
            w = f'Festival {cycle.number}' if week.number == 51 else f'week {week.number}'
            error_message = " ".join([
                f"DAY: {day} is invalid for {w}.",
                f"Must be between 1 and {max_days} inclusive."
            ])
            raise CalmarendianDateError(error_message)
        return day

    def name(self) -> str:
        """
        Return the long name of the day.
        """
        if self.festival:
            return f"Festival {self.LONG_NUMBERS[self.number - 1]}"
        return self.DAY_NAMES[self.number - 1]

    def short_name(self) -> str:
        """
        Return the short name of the day.
        """
        if self.festival:
            return f"Festival {self.number}"
        return self.name()[:2]
