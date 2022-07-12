from typing import Union


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

