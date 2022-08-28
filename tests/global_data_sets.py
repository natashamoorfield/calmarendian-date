from dataclasses import dataclass, field
from typing import List

from npm_calmarendian_date.c_date_config import CDateConfig
from npm_calmarendian_date.exceptions import CalmarendianDateError


@dataclass
class CDateDataItem:
    adr: int
    base_elements: tuple
    csn: str
    dsn: str
    exc_type: Exception.__class__ = Exception
    exc_msg: str = ""
    gcn: str = field(init=False)

    def __post_init__(self):
        self.gcn = "{:02}-{:03}-{}-{:02}-{}".format(*self.base_elements[:5])


c_date_data: List[CDateDataItem] = [
    CDateDataItem(
        adr=CDateConfig.MIN_ADR,
        base_elements=(0, 1, 1, 1, 1, 0, 0, 0, 0, 0),
        csn="699-1-01-1 BZ",
        dsn="1 Midwinter 699 BZ"
    ),
    CDateDataItem(
        adr=-30_825,
        base_elements=(0, 688, 4, 5, 6, 0, 0, 0, 0, 0),
        csn="012-4-05-6 BZ",
        dsn="34 Perihelion 12 BZ"
    ),
    CDateDataItem(
        adr=0,
        base_elements=(0, 700, 7, 51, 8, 0, 0, 0, 0, 0),
        csn="000-7-51-8 BZ",
        dsn="358 Onset 0 BZ"
    ),
    CDateDataItem(
        adr=1,
        base_elements=(1, 1, 1, 1, 1, 0, 0, 0, 0, 0),
        csn="001-1-01-1",
        dsn="1 Midwinter 1"
    ),
    CDateDataItem(
        adr=1_035_926,
        base_elements=(1, 423, 1, 23, 4, 0, 0, 0, 0, 0),
        csn="423-1-23-4",
        dsn="158 Midwinter 423"
    ),
    CDateDataItem(
        adr=1_718_111,
        base_elements=(2, 1, 1, 2, 3, 0, 0, 0, 0, 0),
        csn="701-1-02-3",
        dsn="10 Midwinter 701"
    ),
    CDateDataItem(
        adr=1_719_511,
        base_elements=(2, 1, 5, 2, 3, 0, 0, 0, 0, 0),
        csn="701-5-02-3",
        dsn="10 High Summer 701"
    ),
    CDateDataItem(
        adr=1_905_361,
        base_elements=(2, 77, 3, 4, 5, 0, 0, 0, 0, 0),
        csn="777-3-04-5",
        dsn="26 Spring 777"
    ),
    CDateDataItem(
        adr=CDateConfig.APOCALYPSE_EPOCH_ADR,
        base_elements=(2, 77, 7, 2, 7, 0, 0, 0, 0, 0),
        csn="777-7-02-7",
        dsn="14 Onset 777"
    ),
    CDateDataItem(
        adr=1_906_784,
        base_elements=(2, 77, 7, 7, 7, 0, 0, 0, 0, 0),
        csn="777-7-07-7",
        dsn="49 Onset 777"
    ),
    CDateDataItem(
        adr=24_541_844,
        base_elements=(15, 199, 7, 51, 4, 0, 0, 0, 0, 0),
        csn="9999-7-51-4",
        dsn="354 Onset 9999"
    ),
    CDateDataItem(
        adr=CDateConfig.MAX_ADR,
        base_elements=(99, 700, 7, 51, 8, 0, 0, 0, 0, 0),
        csn="69300-7-51-8",
        dsn="358 Onset 69300"
    )
]

c_date_out_of_range: List[CDateDataItem] = [
    # Valid dates within the framework of an infinitely extensible calendar
    # but not within the constraints of grand-cycle notation.
    CDateDataItem(
        adr=-3_324_810,
        base_elements=(-1, 46, 3, 21, 4, 0, 0, 0, 0, 0),
        csn="1354-3-21-4 BZ",
        dsn="144 Spring 1354 BZ",
        exc_type=CalmarendianDateError,
        exc_msg="GRAND CYCLE: -1 is an invalid input. Must be between 0 and 99 inclusive."
    ),
    CDateDataItem(
        adr=CDateConfig.MIN_ADR - 1,
        base_elements=(-1, 700, 7, 51, 8, 0, 0, 0, 0, 0),
        csn="700-7-51-8 BZ",
        dsn="358 Onset 700 BZ",
        exc_type=CalmarendianDateError,
        exc_msg="GRAND CYCLE: -1 is an invalid input. Must be between 0 and 99 inclusive."
    ),
    CDateDataItem(
        adr=CDateConfig.MAX_ADR + 1,
        base_elements=(100, 1, 1, 1, 1, 0, 0, 0, 0, 0),
        csn="69301-1-01-1",
        dsn="1 Midwinter 69301",
        exc_type=CalmarendianDateError,
        exc_msg="GRAND CYCLE: 100 is an invalid input. Must be between 0 and 99 inclusive."
    ),
    CDateDataItem(
        adr=171_374_477,
        base_elements=(100, 523, 4, 32, 1, 0, 0, 0, 0, 0),
        csn="69823-4-32-1",
        dsn="218 Perihelion 69823",
        exc_type=CalmarendianDateError,
        exc_msg="GRAND CYCLE: 100 is an invalid input. Must be between 0 and 99 inclusive."
    ),
]
