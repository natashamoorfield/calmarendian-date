import warnings

from npm_calmarendian_date.exceptions import CalmarendianDateFormatError
from npm_calmarendian_date.c_date_config import CDateConfig
from npm_calmarendian_date.c_date_utils import DateTimeStruct
from typing import Match, Tuple, Union
from math import ceil


class DateString(object):
    """
    The DateString Class

    A class that will take a date string in Grand Cycle Notation or Common Symbolic Notation format and parse it into
    a DateTimeStruct suitable for instantiating a CalmarendianDate object via its from_date_time_struct method.
    """

    def __init__(self, date_string: str):
        """
        Constructor

        Attempt to match the given date string against the RegEx for a GCN or CSN date string and parse the resulting
        Match object into a DateTimeStruct object.

        Raise a `CalmarendianDateFormatError` if date_string is not a parsable
        representation of a Calmarendian date. Note, however, that beyond type checking and RegEx matching,
        this method performs no other validation.
        """
        try:
            pattern_match = CDateConfig.GCN_DATE_STRING_RE.match(date_string)
        except TypeError:
            em = f"DATE STRING: {date_string.__class__} cannot be parsed as a date string."
            raise CalmarendianDateFormatError(em)

        if pattern_match:
            self.dts = self.parsed_gcn_date(pattern_match)
        else:
            pattern_match = CDateConfig.CSN_DATE_STRING_RE.match(date_string)
            if pattern_match:
                self.dts = self.parsed_csn_date(pattern_match)
            else:
                raise CalmarendianDateFormatError(f"DATE STRING: '{date_string}' is an invalid date string.")

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
        gc, c = DateString.normalized_gcn(int(m.group(1)), m.group(5))
        return DateTimeStruct(gc, c, int(m.group(2)), int(m.group(3)), int(m.group(4)))

    @staticmethod
    def normalized_gcn(c: int, era: Union[str, None]) -> Tuple[int, int]:
        """
        Return a (grand_cycle, cycle_in_grand_cycle) pair calculated from the given (cycle, era) pair.

        Note that the process uses the era marker, if set to BZ, to negate the cycle value but
        otherwise the era marker has no effect on the parsing process.
        A separate process `check_era_consistency` raises an appropriate warning if
        the era marker is incompatible with the given cycle number.
        """
        if era is not None:
            era = era.upper()
            if era == "BZ":
                c = -c
            else:
                DateString.check_era_consistency(c, era)
        gc = ceil(c / 700)
        c += 700 * (1 - gc)
        return gc, c

    @staticmethod
    def check_era_consistency(cycle: int, era_marker: str) -> None:
        """
        Raise a warning if the era_marker is inconsistent with the cycle number.
        Do nothing otherwise.
        """
        if era_marker == "CE" and cycle < 501:
            warnings.warn(f"DATE STRING: Cycle {cycle} is not in Current Era", category=UserWarning, stacklevel=3)
        elif era_marker == "BH" and cycle > 500:
            warnings.warn(f"DATE STRING: Cycle {cycle} is not Before History", category=UserWarning, stacklevel=3)
        elif era_marker == "BH" and cycle == 0:
            warnings.warn(f"DATE STRING: Cycle 0 Era is BZ, not BH", category=UserWarning, stacklevel=3)
