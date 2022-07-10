from typing import NamedTuple, Union

from npm_calmarendian_date import CalmarendianDate
from npm_calmarendian_date.exceptions import CalmarendianDateValueError
from npm_calmarendian_date.calmarendian_date import EraMarker


class DayInSeason(NamedTuple):
    cycle: int
    season: int
    day: int
    era: EraMarker = EraMarker.CE

    def date(self) -> CalmarendianDate:
        w = min(51, (self.day - 1) // 7 + 1)
        d = self.day - ((w - 1) * 7)
        em = self.era.name if self.era else ""
        date_string = f"{self.cycle}-{self.season}-{w:02}-{d}{em}"
        return CD2.from_date_string(date_string)

    def __str__(self):
        cd = self.date()
        return f"{self.day} {cd.season.name()} {self.cycle} {self.era.name}"


class CD2(CalmarendianDate):
    @staticmethod
    def from_day_in_season(cycle: int,
                           season: int,
                           day_in_season: int,
                           era: Union[str, EraMarker] = EraMarker.CE):
        if isinstance(era, str):
            try:
                era = EraMarker[era.upper()]
            except KeyError:
                raise CalmarendianDateValueError(f"Unknown era: {era}")
        return DayInSeason(cycle, season, day_in_season, era).date()

    def day_in_season(self) -> DayInSeason:
        cycle, era = self.absolute_cycle_ref()
        _day_in_season = (self.week.number - 1) * 7 + self.day.number
        return DayInSeason(cycle, self.season.number, _day_in_season, era)


if __name__ == "__main__":
    data = (777, 7, 7)

    dsn_date: DayInSeason = DayInSeason(*data)
    print(dsn_date)

    my_date = dsn_date.date()
    print(my_date)
    print(dsn_date.date().colloquial_date())

    for i, component in enumerate(dsn_date):
        print(i, component)

    dx = CD2.from_day_in_season(777, 7, 49, EraMarker.CE)
    print(type(dx))
    print(dx)

    dy = CD2.from_date_string("777-7-03-1")
    print(dy)
    print(dy.day_in_season())
    dz = CD2.from_day_in_season(*dy.day_in_season())
    print(dz)
    assert dy == dz
