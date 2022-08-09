# `npm_calmarendian_date`

*Based upon the documentation for `datetime` in the Python Standard Library, [here](https://docs.python.org/3/library/datetime.html).*

## Constants
`CDateConfig.MIN_ADR`

A number, `-1_718_100`, which is the ordinal value of the earliest date that can be represented by a `CalmarendianDate` object (699-1-01-1 BZ).

`CDateConfig.MAX_ADR`

A number, `170_091_999`, which is the ordinal value of the last date that can be represented by a `CalmarendianDate` object (69300-7-51-8).

## `CalmarendianDate` Objects

A `CalmarendianDate` object represents a date in the [Calendar of Lorelei](https://www.worldanvil.com/w/calmarendi-natasha-moorfield/a/the-calendar-of-lorelei-article) which, although it has been in existence for only around two hundred cycles, may be thought of as extending indefinitely into the past and the future.

Day 1 of the Calendar of Lorelei is Day 1 of Week 1 of Season 1 of Cycle 1 (usually denoted Monday, Week 1 of Midwinter 1); Day 2 is Tuesday, Week 1 of Midwinter 1 and so on.

Day Zero is the day before Day 1 and is the last day of Cycle Zero.

### Default Constructor
```
class npm_calmarendian_date.CalmarendianDate(
    ordinal: int,
    day_ref_descriptor: DayRefDescriptor
)
```

The default constructor takes, as its required argument, an integer representing the *Absolute Day Reference* (ADR) or the *Apocalypse Reckoning Reference (ARR)* of the date, that being the number of days after Day Zero (or before Day Zero for negative values) or the number of after (or before) the Apocalypse Epoch that the date lies.

It is equivalent to `classmethod date.fromordinal(ordinal, desc)`

Although the calendar is conceptually infinite in both directions, for reasons explained [elsewhere](https://www.worldanvil.com/w/calmarendi-natasha-moorfield/a/collating-calmarendian-dates-article), there are practical limits imposed by the notation used and these limits are respected by  the `CalmarendianDate` class which constrains the `adr_orninal` argument thus:

`CDateConfig.MIN_ADR <= adr_ordinal <= CDateConfig.MAX_ADR`

If an argument outside this range is given, a `CalmarendianDateError` is raised.

The closest CalmarendianDate equivalent of the `date.date(year, month, day` default constructor is the class method `CalmarendianDate.from_numbers(gc, c, s, w, d)`.

### Alternative Constructors

```
classmethod CalmarendianDate.today()
```
This is not a direct equivalent of the `date.today()` method because of how we define what "today" means in terms of Calmarendian world building, namely that it represents the day on which Jennifer and Colette arrived on Calmarendi. It is the snapshot date: everything that takes place before is in the past and everything that happens thereafter is deemed to be the future. `CalmarendianDate.today()`, therefore, always returns the same date: 777-7-03-1.

```
classmethod CalmarendianDate.fromtimestamp(timestanp)
```
We are not implementing an equivalent of the ```date.fromtimestamp()``` constructor at the present time: not until or unless we decide we need some Calmarendian equivalent of the UNIX timestamp.

```
classmethod CalmarendianDate.fromordinal(
    ordinal: int,
    day_ref_descriptor: DayRefDescriptor)
```
The default CalmarendianDate constructor is already an equivalent of the Gregorian `date.fromordinal` class method. Adding this explicit class method, however, not only allows better completeness of method equivalence, it also allows a single, dynamic "from ordinal" that can take either (any) type of ordinal date reference. It shall, therefore, have an inverse method `CalmarendianDate.toordinal`.

```
classmethod CalmarendianDate.fromisoformat(date_string: str)
```
This constructor will not be implemented: "iso format" has no meaning in a calmarendian context. The equivalent constructor is `CalmarendianDate.from_date_string(date_string: str)`.

```
classmethod CalmarendianDate.from_day_in_season(
    cycle: int,
    season: int,
    day-in-season: int,
    era_marker: Union[str, EraMarker] = EraMarker.CE
)
```
Day-in-Season notation (DSN) is a notation which merges the day-in-week and week-in-season values into a single day-in-season value so that, for example, Tuesday, Week 2 of Onset 777 becomes 9 Onset 777. This is to mirror the notation used in the WA Chronology feature rather than being an alternative notation used by Calmarendians themselves.

*Note that while the World Anvil Chronicle feature can replicate the three leap days of every seventh festival, it (currently) has no way of adding the eighth Festival (leap) day that is added to every 700th cycle. This will cause a discrepancy between most dates in the WA Chronicles and a properly implemented DSN here. It will be one day during our period of interest (Grand Cycle 2) and can be compensated for.  It does mean that nothing could ever happen on Festival 8, but why would it? Everyone will be blind drunk after the previous seven straight days of partying!*

Whilst not an exact like-for-like, this should be treated as the CalmarendianDate equivalent of the Gregorian `date.fromisocalendar` method.

It shall have an inverse method: `CalmarendianDate.day_in_season`.

```
classmethod CalmarendianDate.min_date()
```
In the Gregorian `date` class this is implemented as a class attribute `date.min`; we will be implementing it as a class method, equivalent to `CalmarendianDate(CDateConfig.MIN_ADR)`.

```
classmethod CalmarendianDate.max_date()
```
In the Gregorian `date` class this is implemented as a class attribute `date.max`; we will be implementing it as a class method, equivalent to `CalmarendianDate(CDateConfig.MAX_ADR)`.

### Class Attributes
```
CalmarendianDate.resolution
```
The smallest possible difference between non-equal date objects, which is one day, represented by `CalmarendianTimeDelta(days=1)`.

### Instance Attributes

The `year`, `month` and `day` integer attributes have no direct equivalents in a `CalmarendianDate` object. Instead, the primary instance attribute is the absolute day reference (a private attribute) and the derived attributes `grand_cycle`, `cycle`, `season`, `week` and `day`, which, in turn are instances of the various date element classes `GrandCycle`, `CycleInGrandCydle`, `Season`, `Week` and `Day` respectively.

The Calmarendian analogues of `date.year`, `date.month` and `date.day` are thus `CalmarendianDate.grand_cycle.number`, `CalmarendianDate.cycle.number`, `CalmarendianDate.season.number`, `CalmarendianDate.week.number` and `CalmarendianDate.day.number`.

### Instance Properties

```
CalmareandianDate.adr
```
Return the ordinal absolute day reference of the date, where the date 001-1-01-1 (Monday, Week 1 of Midwinter 1) has ordinal 1.

```
CalmareandianDate.apocalypse_reckoning
```
Return the ordinal apocalypse reckoning reference of the date, where the date 777-7-03-1 (Monday, Week 3 of Onset 777) has ordinal 1.

### Supported Operators
#### Comparators
Comparison operators have been fully implemented. Two `CalmarendianDate` objects are said to be equal to one another if and only if they represent the same date on the Calendar of Lorelei. `date1` is said to be less than `date2` if and only if it falls before `date2` on the Calendar of Lorelei.

#### Addition and Subtraction
Addition and subtraction operators are not being implemented in version 1.0.0.

### Instance Methods
```
CalmarendianDate.replace(
    grand_cycle: int = self.grand_cycle.number,
    cycle: int = self.cycle.number,
    season: int = self.season.number,
    week: int = self.week.number,
    day: int = self.day.number
) -> CalmarendianDate
```
Return a date with the same value, except for those parameters given new values by whichever keyword arguments are specified.

Although CalmarendianDate objects are not strictly immutable, this method does not change the current instance, it returns a fresh object with the new value.

```
CalmarendianDate.to_date_time_struct()
```
An equivalent of the Gregorian `date.timetuple()` method, `CalmarendianDate.to_date_time_struct()` returns a `npm_calmarendian_date.c_date_utils.DateTimeStruct` object containing all the elements needed to completely define a Calmarendian date-time object.

```
CalmarendianDate.toordinal(day_ref_descriptor: DayRefDescriptor)
```
When called without an argument or with the default argument `DayRefDescriptor.ADR` this method is the exact equivalent of `CalmarendianDate.adr`. When called with the argument `DayRefDescriptor.ARR` it is the exact equivalent of `CalmarendianDate.apocalypse_reckoning`.

 This method is the inverse of `CalmarendianDAte.fromordinal()` thus, for any date object d: `CalmarednianDate.fromordinal(d.toordinal()) == d`.

```
CalmarendianDate.weekday()
CalmarendianDate.isoweekday()
```
These methods will not be implemented: they have no real equivalence in the Calendar of Lorelei as the day-in-week number is an integral part of the date representation. If the value is required it can be obtained from the `CalmarendianDate.Day.number` property.

```
CalmarendianDate.day_in_season()
```
Return a named tuple object with four components: `cycle`, `season`, `day`, `era_marker`. This is the inverse of `CalmarendianDate.from_day_in_season`, thus for any date object d: `CalmarendianDate.from_day_in_season(*d.day_in_season()) == d`. Whilst not an exact like-for-like, this method should be treated as the CalmarendianDate equivalent of the Gregorian `date.isocalendar` method which, otherwise, has no meaningful equivalence.


```
CalmarendianDate.__str__()
```
Return a string representation of the date in Common Symbolic Notation (CSN). As such, this magic method is an exact equivalent of `CalmarendianDate.csn()`. For more control over when an EraMarker is displayed it is necessary to use the more verbose `CalmarendianDate.common_symbolic_notation()` method.


```
CalmarendianDate.ctime()
```
This method will not be implemented. There is, of course, no underlying C equivalent in the CalmarendianDate ecosystem nor any use case for an analogue of the bobbins it produces.

```
CalmarendianDate.strftime(format: str)
```
Return a string representation of the date, controlled by an explicit format string. Format codes referring to hours, minutes or seconds will return 0 values. The complete list of formatting directives is not yet defined.

## `CalmarendianTimeDelta` Objects
The time-delta class and time-delta functionality are not being implemented in v1.0.0 of `npm_calmarendian_date` but the `CalmarendianTimeDelta` class needs to exist to be able to set the `CalmarendianDate.resolution` attribute with a time-delta object.

## `DateTimeStruct` Objects
`npm_calmarendian_date.c_date_utils.DateTimeStruct`

A dataclass to hold the minimum possible data required to uniquely define a date or date-time value. It is analogous to the Python Standard Library `time.time_struct` structure except that:
1. our structure does not ignore fractional seconds (microseconds); 
2. there is no equivalent of the (derived)  `time_struct.tm_wday` value because day-of-the-week is an integral part of a Calmarendian date;
3. there are no equivalents of the `time_struct.tm_yday` (day-of-the-year) or `time_struct.tm_gmtoff` (offset from UTC) fields because they (or their Calmarendian equivalents) are derived, not defining, data. 
4. apart from the fact that daylight saving time is utter BS in almost _any_ context, on an (effectively) perpetually equinoctial planet like Calmarendi, the concept is meaningless.

We currently have no use for this dataclass; it is included only for the sake of equivalence completeness.

The fields defined by `DateTiemStruct` are:
+ `grand-cycle: int` Should take a value in `range(100)`.
+ `cycle: int` Should take a value in `[x + 1 for x in range(700)]`.
+ `season: int` Should take a value in `[x + 1 for x in range(7)]`.
+ `week: int` Should take a value in `[x + 1 for x in range(51)]`.
+ `day: int` Should take a value in `[x + 1 for x in range(8)]`.
+ `hour: int` Should take a value in `range(16)`.
+ `minute: int` Should take a value in `range(64)`.
+ `second: int` Should take a value in `range(64)`.
+ `microsecond: int` Should take a value in `range(1_000_000)`.
+ `tz: int` Should take a value in `[x - 2 for x in range(4)]`.

but note that no type checking or data validation whatsoever is performed on the data. When instantiating a `DateTimeStruct` object, the time elements can be omitted and will default to zero. All this may change if we ever find a use case for these objects.