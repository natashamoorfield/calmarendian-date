from enum import Enum
from functools import total_ordering
from math import floor
from typing import Tuple, Optional

from npm_calmarendian_date.c_date_config import CDateConfig
from npm_calmarendian_date.date_elements import GrandCycle, CycleInGrandCycle, Season, Week, Day
from npm_calmarendian_date.exceptions import CalmarendianDateError
from npm_calmarendian_date.string_conversions import DateString


class EraMarker(Enum):
    BZ = "Before Time Zero"
    BH = "Before History"
    CE = "Current Era"


@total_ordering
class CalmarendianDate(object):
    """
    The CalmarendianDate class is to the Calendar of Lorelei what, in Python terms, date is to Earth's Gregorian
    Calendar. In particular, CalmarendianDate naively assumes that its calendar always was
    (and always will be) in effect even though it demonstrably was not.
    """
    def __init__(self, new_adr: int):
        self.adr = new_adr
        self.grand_cycle, self.cycle, self.season, self.week, self.day = self.elements_from_adr()

    @property
    def adr(self) -> int:
        """
        Return the absolute day reference. for which "adr" is an alias.
        """
        return self._absolute_day_reference

    @adr.setter
    def adr(self, new_value: int):
        """
        Set a new value for the date objects absolute_day_reference (adr).
        :param new_value: Raise an error on any value that cannot be converted to an integer and
        for any value outside the valid date range.
        """
        try:
            new_value = int(new_value)
        except ValueError:
            raise CalmarendianDateError(f"ADR: Cannot convert [{new_value}] to an integer value.")
        except TypeError:
            raise CalmarendianDateError(f"ADR: {new_value.__class__} cannot be converted to an integer value.")
        if new_value < CDateConfig.MIN_ADR or new_value > CDateConfig.MAX_ADR:
            raise CalmarendianDateError(f"ADR: {new_value} is out of range.")

        self._absolute_day_reference = new_value

    @classmethod
    def from_objects(
            cls,
            grand_cycle: GrandCycle,
            cycle: CycleInGrandCycle,
            season: Season,
            week: Week,
            day: Day
    ):
        """
        Create a CalmarendianDate object from date element objects (GrandCycle, Cycle, etc.)
        :param grand_cycle:
        :param cycle:
        :param season:
        :param week:
        :param day:
        :return: A CalmarendianDate object.
        """
        date = cls.__new__(cls)
        date.grand_cycle = grand_cycle
        date.cycle = cycle
        date.season = season
        date.week = week
        date.day = day
        date.adr = sum([
            date.grand_cycle.days_prior(),
            date.cycle.days_prior(),
            date.season.days_prior(),
            date.week.days_prior(),
            date.day.number
        ])
        return date

    @classmethod
    def from_numbers(cls, gc: int, c: int, s: int, w: int, d: int):
        """
        Create a CalmarendianDate object from numerical inputs representing the date elements grand_cycle, cycle, etc.
        by converting the numbers into date element objects which are then passed to the from_objects factory method.
        :param gc: Numeric representation of the grand_cycle number.
        :param c: Numeric representation of the cycle_in_grand_cycle number.
        :param s: Numeric representation of the season number.
        :param w: Numeric representation of the week number.
        :param d: Numeric representation of the day number.
        :return: A CalmarendianDate object.
        """
        grand_cycle = GrandCycle(gc)
        cycle = CycleInGrandCycle(c)
        season = Season(s)
        week = Week(w, season)
        day = Day(d, week, cycle)
        return cls.from_objects(grand_cycle, cycle, season, week, day)

    @classmethod
    def from_date_string(cls, date_string: str):
        """
        For a given date string in Grand Cycle Notation or Common Symbolic Notation, return the corresponding
        CalmarendianDate object.
        :param date_string: A date string in Grand Cycle Notation format.
        :return: A CalmarendianDate object
        """
        s = DateString(date_string)
        return cls.from_numbers(*s.elements())

    @staticmethod
    def cycle_decode(days: int) -> int:
        """
        For the given number of days, return the number of the cycle (within the current grand cycle) within which
        the numbered day falls.
        :param days: A residual number of days, after accounting for the grand-cycle count.
        :return: The cycle number in which the given day falls.
        """
        cycle = floor(days / CDateConfig.DAYS_per_CYCLE)
        while cycle < 700 and CycleInGrandCycle(cycle + 1).days_prior() < days:
            cycle += 1
        return cycle

    def elements_from_adr(self) -> Tuple[GrandCycle, CycleInGrandCycle, Season, Week, Day]:
        """
        Return a CalmarendianDate object's five grand cycle notation elements, as date element objects,
        calculated from the date's absolute day reference (ADR) property.
        """
        residue = self.adr

        # Calculate GRAND_CYCLE
        grand_cycle = GrandCycle(floor((residue - 1) / CDateConfig.DAYS_per_GRAND_CYCLE) + 1)

        # Re-calculate residual days
        residue -= (grand_cycle.number - 1) * CDateConfig.DAYS_per_GRAND_CYCLE

        # Calculate CYCLE
        cycle = CycleInGrandCycle(self.cycle_decode(residue))

        # Re-calculate residual days
        residue -= (cycle.days_prior())

        # Calculate SEASON
        season = Season(min(floor((residue - 1) / 350) + 1, 7))

        # Re-calculate residual days
        residue -= season.days_prior()

        # Calculate WEEK
        week = Week(min(floor((residue - 1) / 7) + 1, 51), season)

        # Re-calculate residual days
        residue -= week.days_prior()

        # Calculate DAY
        day = Day(residue, week, cycle)

        return grand_cycle, cycle, season, week, day

    def absolute_cycle_ref(self) -> Tuple[int, EraMarker]:
        """
        Return the cycle element of the date as a (cycle, era_marker) pair where cycle is the total number of cycles
        before or after Cycle Zero annotated with the appropriate ere marker BZ, BH or CE.
        """
        acr = abs(((self.grand_cycle.number - 1) * 700) + self.cycle.number)
        if self.grand_cycle.number <= 0:
            em = EraMarker.BZ
        elif 1 <= acr <= 500:
            em = EraMarker.BH
        else:
            em = EraMarker.CE
        return acr, em

    def absolute_season_ref(self) -> int:
        """
        Return the absolute season number, that is the number of seasons
        before or after Season 7 of Cycle Zero. Here we are happy for seasons Before Time Zero
        to be represented by negative numbers.
        """
        return sum([
            self.grand_cycle.seasons_prior(),
            self.cycle.seasons_prior(),
            self.season.number
        ])

    def grand_cycle_notation(self) -> str:
        """
        Return the date as a Grand Cycle Notation date string.
        """
        return "{:>02}-{:>03}-{}-{:>02}-{}".format(
            self.grand_cycle.number,
            self.cycle.number,
            self.season.number,
            self.week.number,
            self.day.number
        )

    def common_symbolic_notation(self, era_marker: Optional[str] = None) -> str:
        """
        Return the date as a Common Symbolic Notation date string.
        :param era_marker: If no era marker is supplied, append an era marker only to dates Before Time Zero.
        If 'BH' is specified, append an era marker to all dates before the Current Era.
        If 'CE' is specified, append an era marker to all dates.
        :return: CSN date string.
        """
        acr, em = self.absolute_cycle_ref()
        if isinstance(era_marker, str):
            era_marker = era_marker.upper()
        if era_marker == "CE" or (era_marker == "BH" and em == EraMarker.BH) or em == EraMarker.BZ:
            era_marker = f" {em.name}"
        else:
            era_marker = ""
        return f"{acr:>03}-{self.season.number}-{self.week.number:>02}-{self.day.number}{era_marker}"

    def colloquial_date(self, *,
                        era_marker: Optional[str] = None,
                        verbose: bool = False
                        ) -> str:
        """
        Return the date as a colloquial date string (for example: Monday, Week 7 of Onset 777).
        :param era_marker: A keyword-only argument whether 'CE' and/or 'BH' era markers should be
        explicitly included as part of the return string.
        :param verbose: A keyword-only argument which, if True, will cause the separator between the day-of-the-week
        and the week number to be 'of' rather than a comma, and to display the era marker in its verbose form
        rather than a two letter abbreviation.
        :return: A colloquial date string.
        """
        first_separator = " of" if verbose else ","
        acr, em = self.absolute_cycle_ref()
        if isinstance(era_marker, str):
            era_marker = era_marker.upper()
        if era_marker == "CE" or (era_marker == "BH" and em == EraMarker.BH) or em == EraMarker.BZ:
            era_marker = f" {em.value}" if verbose else f" {em.name}"
        else:
            era_marker = ""
        if self.day.festival:
            if verbose:
                return f"{self.day.name()} of {acr}{era_marker}"
            return f"Festival {self.day.number} of {acr}{era_marker}"
        return f"{self.day.name()}{first_separator} Week {self.week.number} of {self.season.name()} {acr}{era_marker}"

    def gcn(self) -> str:
        return self.grand_cycle_notation()

    def csn(self) -> str:
        return self.common_symbolic_notation()

    # -- DATE COMPARISON -- #

    def __eq__(self, other) -> bool:
        if not isinstance(other, CalmarendianDate):
            return NotImplemented
        return self.adr == other.adr

    def __lt__(self, other) -> bool:
        if not isinstance(other, CalmarendianDate):
            return NotImplemented
        return self.adr < other.adr

    # -- str and repr -- #

    def __str__(self) -> str:
        """
        The default representation of a CalmarendianDate object is the Common Symbolic Notation format that would
        generally be used by Calmarendians themselves.
        """
        return self.csn()

    def __repr__(self) -> str:
        return f"CalmarendianDate({self.adr})"
