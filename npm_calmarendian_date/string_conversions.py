import warnings

from npm_calmarendian_date.exceptions import CalmarendianDateError, CalmarendianDateFormatError
from npm_calmarendian_date.c_date_config import CDateConfig
from typing import Tuple, Match
from math import ceil


class DateString(object):
    """
    The DateString Class

    A class that will take a date string in Grand Cycle Notation or Common Symbolic Notation format and parse it into
    a five-tuple suitable for instantiating a CalmarendianDate object via its from_numbers method.
    """
    NumericGCNSequence = Tuple[int, int, int, int, int]

    def __init__(self, date_string: str):
        """
        Constructor

        Attempts to match the given date string against the RegEx for a GCN or CSN date string.
        Raises an exception if the given date string does not match either format
        otherwise the Match object is passed to the relevant parser to extract the date's numeric GCN
        elements. NOTE: beyond RegEx matching, this method performs no other error checking.

        :param date_string: A date string which should conform to either GCN or CSN format rules.
        """
        try:
            pattern_match = CDateConfig.GCN_DATE_STRING_RE.match(date_string)
        except TypeError:
            raise CalmarendianDateError(f"DATE STRING: {date_string.__class__} cannot be parsed as a date string.")

        if pattern_match:
            self.gc, self.c, self.s, self.w, self.d = self.parsed_gcn_date(pattern_match)
        else:
            pattern_match = CDateConfig.CSN_DATE_STRING_RE.match(date_string)
            if pattern_match:
                self.gc, self.c, self.s, self.w, self.d = self.parsed_csn_date(pattern_match)
            else:
                raise CalmarendianDateFormatError(f"DATE STRING: '{date_string}' is an invalid date string.")

    def elements(self) -> NumericGCNSequence:
        """
        Return the date's GCN numeric elements as a five-tuple.
        """
        return self.gc, self.c, self.s, self.w, self.d

    @staticmethod
    def parsed_gcn_date(m: Match) -> NumericGCNSequence:
        """
        Extract the numeric date elements from the given Match object.

        :param m: A Match object which should already have matched against
        the RegEx for a GCN date string.
        :return: A five-tuple of GCN date elements.
        """
        return int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))

    @staticmethod
    def parsed_csn_date(m: Match) -> NumericGCNSequence:
        """
        Return the numeric date elements from the given Match object.

        Note that the process uses the date's era marker, if set to BZ, to negate the cycle value but
        otherwise the era marker has no effect on the parsing process. A warning is raised, however, if
        the era marker is incompatible with the given cycle number.
        
        :param m: A Match object which should already have matched against
        the RegEx for a CSN date string.
        :return: A five-tuple of GCN date elements.
        """
        c = int(m.group(1))
        if m.group(5):
            era = m.group(5).upper()
            if era == "BZ":
                c = -c
            elif era == "CE" and c < 501:
                warnings.warn(f"DATE STRING: Cycle {c} is not in Current Era", category=UserWarning, stacklevel=3)
            elif era == "BH" and c > 500:
                warnings.warn(f"DATE STRING: Cycle {c} is not Before History", category=UserWarning, stacklevel=3)
            elif era == "BH" and c == 0:
                warnings.warn(f"DATE STRING: Cycle 0 Era is BZ, not BH", category=UserWarning, stacklevel=3)
        gc = ceil(c / 700)
        c += 700 * (1 - gc)
        return gc, c, int(m.group(2)), int(m.group(3)), int(m.group(4))
