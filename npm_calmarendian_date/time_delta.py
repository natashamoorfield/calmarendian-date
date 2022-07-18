import math
from dataclasses import dataclass
from typing import Union

from npm_calmarendian_date.exceptions import CalmarendianDateError


@dataclass
class CarryForwardDataBlock:
    """
    Dataclass holding the various elements that are "carried forward" from one part of a time-delta initialization
    to the next.
    """
    days: int = 0
    fractional_seconds: float = 0.0
    whole_seconds: int = 0
    fractional_microseconds: float = 0.0
    whole_microseconds: int = 0


class CalmarendianTimeDelta(object):
    """
    A CalmarendianTimeDelta object is a measure of time duration which is the difference between
    two date, date-time or time objects to a resolution of one microsecond - one one-millionth of a second.
    Its primary purpose is to add and subtract such durations from a given date/time object.
    """
    RealNumber = Union[int, float]

    __slots__ = ('_days', '_seconds', '_microseconds')

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

        Don't forget, there are 16 hours in a day, 64 minutes in an hour and 64 seconds in a minute.
        """
        # Type check all the arguments
        args = locals()
        for arg, value in args.items():
            if arg != "self" and not isinstance(value, (int, float)):
                real_number_type_str = f"{type(1)} or {type(1.1)}"
                raise CalmarendianDateError(
                    f"TIMEDELTA: Argument '{arg}' must be {real_number_type_str}, not {type(value)}")

        # We do not check values at this stage because all arguments can be arbitrarily large (or small)
        # but we will consolidate everything into just days, seconds and microseconds
        seconds += ((hours * 64) + minutes) * 64
        microseconds += milliseconds * 1000

        if isinstance(days, float):
            fractional_days, whole_days = math.modf(days)
            fractional_seconds_cf, whole_seconds = math.modf(fractional_days * 16 * 4096)
            whole_days_cf = int(whole_days)
            whole_seconds_cf = int(whole_seconds)
        else:
            fractional_seconds_cf = 0.0
            whole_seconds_cf = 0
            whole_days_cf = days

        if isinstance(seconds, float):
            fractional_seconds, whole_seconds = math.modf(seconds)
            whole_seconds_cf += int(whole_seconds)
            fractional_seconds_cf += fractional_seconds
        else:
            whole_seconds_cf += seconds

        fractional_seconds_cf, extra_seconds = math.modf(fractional_seconds_cf)
        whole_seconds_cf += int(extra_seconds)

        extra_days, whole_seconds_cf = divmod(whole_seconds_cf, 16 * 4096)
        whole_days_cf += extra_days

        fractional_microseconds_cf, whole_microseconds = math.modf(fractional_seconds_cf * 1_000_000)
        whole_microseconds_cf = int(whole_microseconds)

        if isinstance(microseconds, float):
            fractional_microseconds, whole_microseconds = math.modf(microseconds)
            whole_microseconds_cf += int(whole_microseconds)
            fractional_microseconds_cf += fractional_microseconds
        else:
            whole_microseconds_cf += microseconds

        extra_microseconds = round(fractional_microseconds_cf)
        whole_microseconds_cf += extra_microseconds

        extra_seconds, whole_microseconds_cf = divmod(whole_microseconds_cf, 1_000_000)
        whole_seconds_cf += extra_seconds

        extra_days, whole_seconds_cf = divmod(whole_seconds_cf, 16 * 4096)
        whole_days_cf += extra_days

        self.days = whole_days_cf
        self.seconds = whole_seconds_cf
        self.microseconds = whole_microseconds_cf

    @property
    def days(self):
        return self._days

    @days.setter
    def days(self, new_value: int):
        if not isinstance(new_value, int):
            raise CalmarendianDateError(f"TIMEDELTA: internally, days must be of type 'int' not {type(new_value)}")
        self._days = new_value

    @property
    def seconds(self):
        return self._seconds

    @seconds.setter
    def seconds(self, new_value: int):
        self._seconds = new_value

    @property
    def microseconds(self):
        return self._microseconds

    @microseconds.setter
    def microseconds(self, new_value: int):
        self._microseconds = new_value

    def __str__(self):
        mm, ss = divmod(self._seconds, 64)
        hh, mm = divmod(mm, 64)
        out_string = f"{hh:02}:{mm:02}:{ss:02}"
        if self._microseconds:
            out_string = f"{out_string}.{self._microseconds:06}"
        if self._days:
            s = "" if abs(self._days) == 1 else "s"
            out_string = f"{self._days} day{s} + {out_string}"
        return out_string
