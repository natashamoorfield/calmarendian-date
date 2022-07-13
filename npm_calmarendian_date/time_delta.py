import math
from typing import Union

from npm_calmarendian_date.exceptions import CalmarendianDateError


class CalmarendianTimeDelta(object):
    """
    A CalmarendianTimeDelta object is a measure of time duration which is the difference between
    two date, date-time or time objects to a resolution of one microsecond - one one-millionth of a second.
    Its primary purpose is to add and subtract such durations from a given date/time object.
    """
    RealNumber = Union[int, float]

    def __init__(
            self,
            *,
            days: RealNumber = 0,
            hours: RealNumber = 0,
            minutes: RealNumber = 0,
            seconds: RealNumber = 0,
            milliseconds: RealNumber = 0,
            microseconds: RealNumber = 0
    ):
        """
        The default constructor.

        A new CalmarendianTimeDelta can be specified using any combination of days, hours, minutes, seconds,
        milliseconds and microseconds. Each component is optional, can be specified as positive or negative and
        given as an arbitrarily large float or integer value. Omitted components all default to zero.

        Be aware that whatever combination of components are given, the internal representation of a time delta is
        normalized to a standard and unique representation given by days, seconds and microseconds.
        This choice of components is based upon that used in the Gregorian
        timedelta class and it, apparently, is entirely arbitrary.

        The normalization process will result in values constrained thus:
        0 <= microseconds < 1e6
        0 <= seconds < 2 ** 16
        -171_810_100 <= days < 171_810_100

        The normalization process ensures that the microseconds and seconds components do not overflow their bounds;
        if days exceeds its constraints, a CalmarendianDateRangeError is raised.

        Note that the representation of negative durations can appear counterintuitive
        with a duration of -1 microseconds, for example, being
        represented as (days = -1, seconds = 65535, microseconds = 999999) which could be thought of as one day back,
        65,535.999999 seconds forward.
        """
        try:
            seconds += ((hours * 64) + minutes) * 64
        except TypeError:
            raise CalmarendianDateError("Timedelta hours, minutes and seconds must be of type 'int' or 'float'.")
        try:
            microseconds += milliseconds * 1000
        except TypeError:
            raise CalmarendianDateError("Timedelta milliseconds and microseconds must be of type 'int' or 'float'.")

        if isinstance(days, float):
            fractional_days, whole_days = math.modf(days)
            fractional_seconds_cf, whole_seconds = math.modf(fractional_days * 16 * 4096)
            whole_days = int(whole_days)
            whole_seconds_cf = int(whole_seconds)
        elif isinstance(days, int):
            fractional_seconds_cf = 0.0
            whole_seconds_cf = 0
            whole_days = days
        else:
            raise CalmarendianDateError(f"Timedelta days must be a real number, not {days}.")

        self.days = whole_days
        self.seconds = whole_seconds_cf
        self.microseconds = int(fractional_seconds_cf)

