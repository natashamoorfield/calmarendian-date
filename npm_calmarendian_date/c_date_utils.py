"""
Common utility functions and classes used in various parts of the library.
"""
import math
from dataclasses import dataclass
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


@dataclass
class DateTimeStruct(object):
    """
    A structure to hold the minimum possible data required to uniquely identify a date, time of date-time value.

    it is analogous to the standard Python time.time_struct named tuple (particularly in that is appears to serve
    no real purpose) except that (i) only integer values are stored, fractional seconds are represented as
    microseconds; (ii) there is no weekday value (in Calmarendian dates, the day-of-the-week is an integral part of
    the date; (iii) day-of-the-cycle (equivalent to day-of-the-year) and standard time offset are omitted - they are
    derived, not defining, data; (iv) apart from the fact that daylight saving time is utter BS in almost any
    circumstances, on an (effectively) equinoctial planet, the concept is completely meaningless.
    """
    pass
