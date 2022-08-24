import re


class CDateConfig(object):
    """
    Class serving as a namespace for constants used in CalmarendianDate.
    """

    # The lowest and highest values the Absolute Day Reference of any date can take.
    # Derived from the earliest and latest dates that can be represented in Grand Cycle Notation:
    # 00-001-1-01-1 and 99-700-7-51-8 respectively.
    MIN_ADR: int = -1_718_100
    MAX_ADR: int = 170_091_999

    # The maximum Δt (in days) that can exist between two dates or date-times:
    MAX_DELTA_DAYS: int = 171_810_100

    # Scale Factors
    DAYS_per_GRAND_CYCLE: int = 1_718_101
    DAYS_per_CYCLE: float = DAYS_per_GRAND_CYCLE / 700
    SECONDS_per_DAY: int = 16 * 64 * 64  # Could also be expressed as 2 ** 16
    MICROSECONDS_per_SECOND: int = 1_000_000

    # Regex representation of Grand Cycle and Common symbolic Notations
    GCN_DATE_STRING_RE = re.compile(r'^(\d{2})-([0-7]\d{2})-([1-7])-([0-5]\d)-([1-8])$')
    CSN_DATE_STRING_RE = re.compile(r'^((?:[1-9]|[1-6]\d)?\d{3})-([1-7])-([0-5]\d)-([1-8]) *(BZ|BH|CE)?$',
                                    re.IGNORECASE)
    DSN_DATE_STRING_RE = re.compile(r"^(\d{1,3})[ -]+([A-Z]+(?: [A-Z]+)*|[1-7])[ -]+(\d{1,5})[ -]*(BZ|BH|CE)?$",
                                    re.IGNORECASE)
    """
    Note that whereas GCN and CSN date strings must conform strictly to the relevant format specification, 
    there is more flexibility with DSN strings in that: 
    numbers do not need to be zero padded but can be (up to the maximum length of the relevant value); 
    the season can be specified as a number or a name; 
    the name can be arbitrarily shortened to its first n characters; 
    the separators can be any combination of spaces and dashes 
    but cannot be omitted except between the cycle number and era marker.
    Spaces that are part of the Season name are not interpreted as separators.
    """

    # Epoch for Apocalypse Reckoning (Day Zero (AR 0)) is 777-7-02-7.
    # Note that Day One of the Apocalypse (AR 1),
    # the day on which Jennifer and Colette actually arrived, is 777-7-03-1
    APOCALYPSE_EPOCH_ADR: int = 1_906_749
