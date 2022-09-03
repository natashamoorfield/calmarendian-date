"""
Common utility functions and classes used in various parts of the library.
"""
import math
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Union, Tuple

from npm_calmarendian_date.date_elements import GrandCycle, CycleInGrandCycle

RealNumber = Union[int, float]


def split_float(x: RealNumber) -> Tuple[int, float]:
    """
    Wrapper function for the standard math.modf() method.

    Returns the integer and fractional parts of the argument as a two-tuple but, more intuitively, with
    the integer part first, converted to an integer type. Within the context of the CalmarendianTimeDelta class
    we always need the whole part specifically to be an integer, not a float.
    """
    fractional_part, whole_part = math.modf(x)
    return int(whole_part), fractional_part


def round_half_away_from_zero(number: RealNumber) -> int:
    """
    Return the value of the given number rounded to the nearest integer, rounding away from zero on halves.

    The default behaviour of Python's built-in round function (and, by extension, the way in which Python
    rounds its own time-deltas) is to round halves to the nearest even integer. This is not what we want.
    """
    wp, fp = split_float(abs(number))
    if fp >= 0.5:
        wp += 1
    # Restore the sign before returning...
    return wp * (-1 if number < 0 else +1)


@dataclass(frozen=True)
class DateTimeStruct(object):
    """
    A dataclass to hold the minimum possible data required to uniquely define a date or date-time value.

    It is analogous to the Python Standard Library `time.time_struct` data structure.
    We currently have no use for this class;
    it is included only for the sake of equivalence completeness.

    Note that no type checking or data validation whatsoever is performed on the data.
    When instantiating a `DateTimeStruct` object, the time elements can be omitted and will default to zero.
    All this may change if we ever find a use case for these objects.
    """
    grand_cycle: int
    cycle: int
    season: int
    week: int
    day: int
    hour: int = 0
    minute: int = 0
    second: int = 0
    microsecond: int = 0
    tz: int = 0


class EraMarker(Enum):
    BZ = "Before Time Zero"
    BH = "Before History"
    CE = "Current Era"


class AbsoluteCycleRef(object):
    """
    Given a (grand_cycle, cycle_in_grand_cycle) pair will create a representation of the cycle
    comprising the absolute cycle number, relative to cycle zero, with an era marker. And vice versa.
    """
    def __init__(self, grand_cycle: GrandCycle, cycle_in_grand_cycle: CycleInGrandCycle):
        self.cycle = abs(((grand_cycle.number - 1) * 700) + cycle_in_grand_cycle.number)
        self.era_marker = self.calculated_era_marker(grand_cycle.number)

    def calculated_era_marker(self, grand_cycle: int) -> EraMarker:
        if grand_cycle <= 0:
            return EraMarker.BZ
        if 1 <= self.cycle <= 500:
            return EraMarker.BH
        return EraMarker.CE

    @classmethod
    def from_cycle_era(cls, cycle: Union[int, str], era_marker_str: Union[str, None]):
        """
        Return an AbsoluteCycleRef object from raw data.

        The cycle and era_marker_str arguments are assumed to have come from a date string that has been matched
        against RegEx or similarly validated as (the string representation of) an unsigned integer
         and one of BZ|BH|CE|None.
        """
        acr = cls.__new__(cls)
        acr.cycle = int(cycle)
        if era_marker_str is None:
            acr.era_marker = "BH" if 1 <= acr.cycle <= 500 else "CE"
        else:
            acr.era_marker = EraMarker[era_marker_str.upper()]
            acr.check_era_consistency()
        return acr

    def normalized_gc_cgc(self) -> Tuple[int, int]:
        """
        Return a (grand_cycle, cycle_in_grand_cycle) pair calculated from the object's (cycle, era) pair.

        Note that the process uses the era marker, if set to BZ, to negate the cycle value but
        otherwise the era marker has no effect on the parsing process.
        """
        sign = -1 if self.era_marker == EraMarker.BZ else +1
        relative_cycle_number = sign * self.cycle
        gc = math.ceil(relative_cycle_number / 700)
        cgc = relative_cycle_number + (700 * (1 - gc))
        return gc, cgc

    def check_era_consistency(self) -> None:
        """
        Raise a warning if the era_marker is inconsistent with the cycle number.
        Do nothing otherwise.
        """
        if self.era_marker == EraMarker.CE and self.cycle < 501:
            warnings.warn(f"DATE STRING: Cycle {self.cycle} is not in Current Era.", category=UserWarning, stacklevel=3)
        elif self.era_marker == EraMarker.BH and self.cycle > 500:
            warnings.warn(f"DATE STRING: Cycle {self.cycle} is not Before History.", category=UserWarning, stacklevel=3)
        elif self.era_marker == EraMarker.BH and self.cycle == 0:
            warnings.warn(f"DATE STRING: Cycle 0 Era is BZ, not BH.", category=UserWarning, stacklevel=3)

    # TODO Implement a __str__ method to return a printable representation of the (cycle, era_marker) pair.
