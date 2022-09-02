"""
Common utility functions and classes used in various parts of the library.
"""
import math
from dataclasses import dataclass
from enum import Enum
from typing import Union, Tuple

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
    comprising the absolute cycle number, relative to cycle zero, with an era marker.
    """
