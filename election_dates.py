from npm_calmarendian_date.calmarendian_date import CalmarendianDate


class Election(object):
    """
    Class that will generate information about an election for a given cycle/season.
    """
    def __init__(self, cycle: int, season: int):
        self.election_date = CalmarendianDate.from_date_string(f"{cycle:>03}-{season}-25-1")

    def election_season(self):
        """
        Return a string with the season name and cycle number.
        """
        return f"{self.election_date.season.name()} {self.election_date.absolute_cycle_ref()[0]}"

    def election_tiers(self) -> str:
        """
        Calculate which tiers of government will have elections in the given season and
        return a string listing those tiers.
        """
        tiers = []
        asr = self.election_date.absolute_season_ref()
        if asr % 4 == 1:
            tiers.append("Provincial")
        if asr % 3 == 1:
            tiers.append("County")
        if asr % 2 == 1:
            tiers.append("District")
        item_count = len(tiers)
        if item_count == 0:
            return "-- none --"
        out_string = ""
        for i, item in enumerate(tiers):
            if i + 1 == item_count:
                out_string += item
            elif i + 2 == item_count:
                out_string += item + " and "
            else:
                out_string += item + ", "
        return out_string


class ElectoralCycle(object):
    """
    Class for generating a sequence of Election objects for the required time period.
    By default, it will generate election objects for all seven seasons in the specified Cycle.
    Optionally it can be extended to an arbitrary number of Cycles.
    """
    def __init__(self, first_cycle: int, *, cycles: int = 1):
        self.start = first_cycle
        self.cycles = cycles

    def elections(self):
        """
        Generator yielding sequential Election objects.
        """
        count = 0
        while count < self.cycles:
            season = 1
            while season < 8:
                yield Election(self.start + count, season)
                season += 1
            count += 1


class Application(object):
    """
    An application to display details of seasonal elections in the Western Provinces.
    An application to illustrate the use of the npm_calmarendian_date package.
    """
    def __init__(self):
        self.election_cycle = ElectoralCycle(777, cycles=2)

    def run(self):
        """
        Print out the election schedule for the given period.
        """
        print("Season               Date          Elections")
        for e in self.election_cycle.elections():
            print(f"{e.election_season():<20} {e.election_date}    {e.election_tiers()}")


if __name__ == '__main__':
    app = Application()
    app.run()
