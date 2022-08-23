from dataclasses import dataclass, field

from npm_calmarendian_date.c_date_config import CDateConfig


@dataclass
class CDateDataItem:
    adr: int
    base_elements: tuple
    csn: str
    dsn: str
    gcn: str = field(init=False)

    def __post_init__(self):
        self.gcn = "{:02}-{:03}-{}-{:02}-{}".format(*self.base_elements[:5])


c_date_data = [
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
        adr=1_905_361,
        base_elements=(2, 77, 3, 4, 5, 0, 0, 0, 0, 0),
        csn="777-3-04-5",
        dsn="26 Spring 777"
    ),
    CDateDataItem(
        adr=CDateConfig.APOCALYPSE_EPOCH_ADR,
        base_elements=(2, 77, 7, 2, 7, 0, 0, 0, 0, 0),
        csn="777-7-02-7",
        dsn="21 Onset 777"
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
