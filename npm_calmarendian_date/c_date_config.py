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

    # Scale Factors
    DAYS_per_GRAND_CYCLE: int = 1_718_101
    DAYS_per_CYCLE: float = DAYS_per_GRAND_CYCLE / 700

    # Regex representation of Grand Cycle and Common symbolic Notations
    GCN_DATE_STRING_RE = re.compile(r'^(\d{2})-([0-7]\d{2})-([1-7])-([0-5]\d)-([1-8])$')
    CSN_DATE_STRING_RE = re.compile(r'^([1-9]?\d{3})-([1-7])-([0-5]\d)-([1-8]) *(BZ|BH|CE)?$', re.IGNORECASE)

    # Epoch for Apocalypse Reckoning
    TEMP_BASELINE_ADR: int = 1_907_093  # New Cycle Day 778
    APOCALYPSE_EPOCH_ADR: int = TEMP_BASELINE_ADR
    # TODO: Determine the correct epoch day for Apocalypse Reckoning:
    #  the day Jennifer and Colette arrived on Calmarendi.
    #  https://github.com/natashamoorfield/npm_calmarendian_date/issues/4
