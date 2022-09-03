import warnings

from npm_calmarendian_date.exceptions import CalmarendianDateFormatError
from npm_calmarendian_date.c_date_config import CDateConfig
from npm_calmarendian_date.c_date_utils import DateTimeStruct, AbsoluteCycleRef
from npm_calmarendian_date.date_elements import Season
from typing import Match, Tuple, Union
from math import ceil


class DateString(object):
    """
    The DateString Class

    A class that will take a date string in Grand Cycle Notation, Common Symbolic Notation or Day-in-Season format and
     parse it into a DateTimeStruct for instantiating a CalmarendianDate object via its from_date_time_struct method.
    """

    SEP_CHARS = " -"

    def __init__(self, date_string: str):
        """
        Constructor

        Store the original date string and construct a DateTimeStruct from it.
        """
        self.original_string = date_string
        self.raw_data = self.stripped_date_string()
        self.dts = self.parsed_date_string()

    def stripped_date_string(self):
        """
        Return a string stripped of any characters that can be interpreted as valid date element separators.

        Raise a `CalmarendianDateFormatError` if the input object cannot be stripped (that is, it is not a string)
        or if the stripped string has zero length.
        """
        try:
            useful_chars = self.original_string.strip(DateString.SEP_CHARS)
        except AttributeError:
            em = f"DATE STRING must be 'str', not '{self.original_string.__class__.__name__}'."
            raise CalmarendianDateFormatError(em)
        if len(useful_chars) == 0:
            em = f"DATE STRING '{self.original_string}' is devoid of useful data."
            raise CalmarendianDateFormatError(em)
        return useful_chars

    def parsed_date_string(self) -> DateTimeStruct:
        """
        Attempt to match the given date string against the RegEx for a GCN, CSN or DSN date string and
        parse the resulting Match object into a DateTimeStruct object.

        Raise a `CalmarendianDateFormatError` if date_string is not a parsable representation of a Calmarendian date.
        Note, however, that beyond basic type checking and RegEx matching,
        this method performs no other validation.
        """
        try:
            pattern_match = CDateConfig.GCN_DATE_STRING_RE.match(self.raw_data)
        except TypeError:
            em = f"DATE STRING must be 'str', not '{self.original_string.__class__.__name__}'."
            raise CalmarendianDateFormatError(em)
        if pattern_match:
            return self.parsed_gcn_date(pattern_match)

        pattern_match = CDateConfig.CSN_DATE_STRING_RE.match(self.raw_data)
        if pattern_match:
            return self.parsed_csn_date(pattern_match)

        pattern_match = CDateConfig.DSN_DATE_STRING_RE.match(self.raw_data)
        if pattern_match:
            return self.parsed_dsn_date(pattern_match)

        raise CalmarendianDateFormatError(f"DATE STRING: '{self.raw_data}' is not a valid date string.")

    @staticmethod
    def parsed_gcn_date(m: Match) -> DateTimeStruct:
        """
        Return a `DateTimeStruct` constructed from the elements of the passed Match object.
        The Match object `m` must be the positive result of matching a date string against the GCN RegEx.
        """
        return DateTimeStruct(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))

    @staticmethod
    def parsed_csn_date(m: Match) -> DateTimeStruct:
        """
        Return a `DateTimeStruct` constructed from the elements of the passed Match object.
        The Match object `m` must be the positive result of matching a date string against the CSN RegEx.
        """
        gc, cgc = AbsoluteCycleRef.from_cycle_era(m.group(1), m.group(5)).normalized_gc_cgc()
        return DateTimeStruct(gc, cgc, int(m.group(2)), int(m.group(3)), int(m.group(4)))

    @staticmethod
    def parsed_dsn_date(m: Match) -> DateTimeStruct:
        """
        Return a `DateTimeStruct` constructed from the elements of the passed Match object.
        The Match object `m` must be the positive result of matching a date string against the DSN RegEc.
        """
        gc, cgc = AbsoluteCycleRef.from_cycle_era(m.group(3), m.group(4)).normalized_gc_cgc()
        s = Season.from_name(m.group(2)).number
        w, d = DateString.split_day_in_season(int(m.group(1)))
        return DateTimeStruct(gc, cgc, s, w, d)

    @staticmethod
    def split_day_in_season(day_in_season: int) -> Tuple[int, int]:
        """
        Return a (week, day) pair from a day-in-season number.

        Note that this method works on the principle of garbage-in-garbage-out.
        It will return results for any integer input value but, intentionally, attempts no validation.
        For input values less than 1 and greater than 358 it will return values that make no sense
        in the context of Calmarendian dates.
        """
        w = min(51, (day_in_season - 1) // 7 + 1)
        d = day_in_season - ((w - 1) * 7)
        return w, d
