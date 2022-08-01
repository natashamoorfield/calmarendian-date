import math
from dataclasses import dataclass
from typing import Union, Tuple

from npm_calmarendian_date.c_date_config import CDateConfig
from npm_calmarendian_date.exceptions import CalmarendianDateError

RealNumber = Union[int, float]


@dataclass
class CarryForwardDataBlock:
    """
    Dataclass holding the various elements that are "carried forward" from one part of a time-delta initialization
    to the next.
    """
    days: int = 0
    seconds: int = 0
    microseconds: RealNumber = 0.0

    def normalize(self) -> None:
        """
        Normalize the data so that:
        0 <= self.microseconds < CDateConfig.MICROSECONDS_per_SECOND
        0 <= self.seconds < CDateConfig.SECONDS_per_DAY
        The magic of the divmod function ensures that all negative microsecond and second values bubble up to the
        day value, ensuring that there is only one representation for any given time-delta.
        """
        self.microseconds = self.round_half_away_from_zero()

        extra_seconds, self.microseconds = divmod(self.microseconds, CDateConfig.MICROSECONDS_per_SECOND)
        self.seconds += extra_seconds

        extra_days, self.seconds = divmod(self.seconds, CDateConfig.SECONDS_per_DAY)
        self.days += extra_days

    def round_half_away_from_zero(self) -> int:
        """
        Return the value of microseconds rounded to the nearest integer, rounding away from zero on halves.

        The default behaviour of Python's built-in round function (and, by extension, the way in which Python
        rounds its own time-deltas) is to round halves to the nearest even integer. This is not what we want.
        """
        wp, fp = CalmarendianTimeDelta.split_float(abs(self.microseconds))
        if fp >= 0.5:
            wp += 1
        # Restore the sign before returning...
        return wp * (-1 if self.microseconds < 0 else +1)


class CalmarendianTimeDelta(object):
    """
    A CalmarendianTimeDelta object is a measure of time duration which is the difference between
    two date, date-time or time objects to a resolution of one microsecond - one one-millionth of a second.
    Its primary purpose is to add and subtract such durations from a given date/time object.

    An interesting facet of the Calmarendian time system (but not one we take advantage of here) is that
    any time period which is a whole number of seconds long has, when expressed as days and fractions of a day,
    an exact binary representation.
    """
    __slots__ = ('_days', '_seconds', '_microseconds', '_hashcode')

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
        All arguments are keyword only.

        Be aware that whatever combination of components are given, the internal representation of a time delta is
        normalized to a standard and unique representation given by days, seconds and microseconds.
        This choice of components is based upon that used in the Gregorian
        timedelta class and it, apparently, is entirely arbitrary.

        The normalization process will result in values constrained thus:
        0 <= microseconds < 1e6 (MICROSECONDS_per_SECOND)
        0 <= seconds < 2 ** 16 (SECONDS_per_DAY)
        -171_810_100 <= days < 171_810_100 (MAX_DELTA_DAYS)

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

        cf = CalmarendianTimeDelta.process_days(days)
        cf = CalmarendianTimeDelta.process_seconds(seconds, cf)
        cf = CalmarendianTimeDelta.process_microseconds(microseconds, cf)
        cf.normalize()

        self._hashcode = None
        self.days = cf.days
        self.seconds = cf.seconds
        self.microseconds = cf.microseconds

    # INIT sub-methods
    @staticmethod
    def process_days(arg_days: RealNumber) -> CarryForwardDataBlock:
        """
        Break apart the 'days' argument into its integer and fractional components.
        Convert the fractional day into seconds, and break that into integer and fractional components.
        Convert the fractional second into microseconds
        So, for example, 1.5 days splits into 1 day, 32768 seconds;
        1.18838 days splits into 1 day, 12345 seconds and 671680 microseconds.
        At this stage, no normalization is performed so -1.5 days splits into -1 days, -32768 seconds
        and -671680 microseconds.
        Return all the derived data via the CarryForwardDataBlock.
        """
        cf = CarryForwardDataBlock()
        cf.days, fractional_days = CalmarendianTimeDelta.split_float(arg_days)
        cf.seconds, fractional_seconds = CalmarendianTimeDelta.split_float(
            fractional_days * CDateConfig.SECONDS_per_DAY)
        cf.microseconds = fractional_seconds * CDateConfig.MICROSECONDS_per_SECOND

        return cf

    @staticmethod
    def process_seconds(arg_seconds: RealNumber, cf: CarryForwardDataBlock) -> CarryForwardDataBlock:
        """
        Break apart the 'seconds' argument into its integer and fractional components.
        Convert the fractional second into microseconds.
        Add the whole seconds and microseconds to the carry-forward data block and return the updated data block.
        """
        ws, fs = CalmarendianTimeDelta.split_float(arg_seconds)
        cf.seconds += ws
        cf.microseconds += fs * CDateConfig.MICROSECONDS_per_SECOND
        return cf

    @staticmethod
    def process_microseconds(arg_microseconds: RealNumber, cf: CarryForwardDataBlock) -> CarryForwardDataBlock:
        """
        Add the value of the 'microseconds' argument to the carry-forward data block and return the updated data block.
        """
        cf.microseconds += arg_microseconds
        return cf

    # Other CONSTRUCTORS
    @classmethod
    def maximum(cls):
        """
        Return the largest allowable time-delta. This has been defined as the maximum possible difference between two
        valid CalmarendianDateTime objects: 171_810_099 days, 65535.999999 seconds.
        """
        return cls(days=171_810_099, seconds=65_535, microseconds=999_999)

    @classmethod
    def minimum(cls):
        """
        Return the negative of the largest allowable time-delta, the normalized representation of which is
        -171_810_100 days + one microsecond.
        It is possible to construct a time-delta of exactly -171_810_100 days but only because
        trapping the error isn't worth the bother.

        The value of CalmarendianTimeDelta.minimum() should not be confused with the smallest possible difference
        between two date-time objects (which is zero) nor with the smallest possible difference between two non-equal
        date-time objects (which is 1 microsecond).
        """
        return cls(days=-171_810_100, microseconds=1)

    @classmethod
    def resolution(cls):
        """
        The smallest possible difference between non-equal timedelta objects which is 1 microsecond.
        """
        return cls(microseconds=1)

    # GETTERS and SETTERS
    @property
    def days(self):
        return self._days

    @days.setter
    def days(self, new_value: int):
        self._common_new_value_checks('days', new_value)
        if new_value < -CDateConfig.MAX_DELTA_DAYS or new_value >= CDateConfig.MAX_DELTA_DAYS:
            raise CalmarendianDateError(f"TIMEDELTA days illegal value: {new_value}.")
        self._days = new_value

    @property
    def seconds(self):
        return self._seconds

    @seconds.setter
    def seconds(self, new_value: int):
        self._common_new_value_checks('seconds', new_value)
        if new_value < 0 or new_value >= CDateConfig.SECONDS_per_DAY:
            raise CalmarendianDateError(f"TIMEDELTA seconds illegal value: {new_value}.")

        self._seconds = new_value

    @property
    def microseconds(self):
        return self._microseconds

    @microseconds.setter
    def microseconds(self, new_value: int):
        self._common_new_value_checks('microseconds', new_value)
        if new_value < 0 or new_value >= CDateConfig.MICROSECONDS_per_SECOND:
            raise CalmarendianDateError(f"TIMEDELTA microseconds illegal value: {new_value}.")

        self._microseconds = new_value

    def total_seconds(self, result_type: str = 'float') -> Union[int, float]:
        """
        Return the duration of the time-delta is seconds.
        Return value can be an int (with microseconds rounded to the nearest second)
        by specifying a return_type of 'int' or as a float (default)
        :param result_type: Can be any of 'i', 'int', 'f', 'float', upper or lower case.
        """
        rt = str(result_type).lower()
        if rt not in ['f', 'float', 'i', 'int']:
            raise CalmarendianDateError(f"TIMEDELTA total_seconds: Bad type specification '{result_type}'.")
        whole_seconds = self.days * CDateConfig.SECONDS_per_DAY + self.seconds
        if rt[0] == 'i':
            return whole_seconds + round(self.microseconds / CDateConfig.MICROSECONDS_per_SECOND)
        us = whole_seconds * CDateConfig.MICROSECONDS_per_SECOND + self.microseconds
        return us / CDateConfig.MICROSECONDS_per_SECOND

    # DUNDER methods
    def __str__(self):
        mm, ss = divmod(self._seconds, 64)
        hh, mm = divmod(mm, 64)
        out_string = f"{hh:02}:{mm:02}:{ss:02}"
        if self._microseconds:
            out_string = f"{out_string}.{self._microseconds:06}"
        if self._days:
            s = "" if abs(self._days) == 1 else "s"
            out_string = f"{self._days:+,} day{s} + {out_string}"
        return out_string

    def __repr__(self):
        dx = dict(days=self.days, seconds=self.seconds, microseconds=self.microseconds)
        arg_strings = [f"{k}={v}" for k, v in dx.items() if v]
        return f"CalmarendianTimeDelta({', '.join(arg_strings)})"

    def __hash__(self):
        """
        The object is hashed only once. After that the values of days, seconds and microseconds cannot be changed.
        """
        if self._hashcode is None:
            self._hashcode = hash(self._get_state())
        return self._hashcode

    def __bool__(self):
        return self._get_state() != (0, 0, 0)

    # COMPARISON methods
    def __eq__(self, other):
        if isinstance(other, CalmarendianTimeDelta):
            return self._compare(other) == 0
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, CalmarendianTimeDelta):
            return self._compare(other) <= 0
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, CalmarendianTimeDelta):
            return self._compare(other) < 0
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, CalmarendianTimeDelta):
            return self._compare(other) >= 0
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, CalmarendianTimeDelta):
            return self._compare(other) > 0
        return NotImplemented

    # UTILITY methods
    @staticmethod
    def split_float(x: RealNumber) -> Tuple[int, float]:
        """
        Wrapper function for the standard math.modf() method.
        Returns the integer and fractional parts of the argument as a two-tuple but, more intuitively, with
        the integer part first, converted to an integer type. Within the context of the CalmarendianTimeDelta class
        we always need the whole part specifically to be an integer, not a float.
        """
        fractional_part, whole_part = math.modf(x)
        return int(whole_part), fractional_part

    def _get_state(self) -> Tuple[int, int, int]:
        """
        Return a tuple containing the days, seconds, microseconds properties of the time-delta
        """
        return self.days, self.seconds, self.microseconds

    def _compare(self, other) -> int:
        """
        Compare two CalmarendianTimeDelta objects and return 0 if they are equal to one another,
        +1 if self is greater than the other and
        -1 if self is less than the other.
        """
        assert isinstance(other, CalmarendianTimeDelta)
        this = self._get_state()
        that = other._get_state()
        if this == that:
            return 0
        if this > that:
            return 1
        return -1

    def _common_new_value_checks(self, name: str, new_value: int) -> None:
        """
        Raise a CalmarendianDateError if the time-delta object has previously been hashed.
        Raise a CalmarendianDateError if the new_value is not an integer.
        Otherwise, do nothing.
        """
        if self._hashcode is not None:
            raise CalmarendianDateError("Cannot change a TIMEDELTA after it has been hashed.")
        if not isinstance(new_value, int):
            raise CalmarendianDateError(
                f"TIMEDELTA: internally, {name} must be of type {type(1)} not {type(new_value)}.")
