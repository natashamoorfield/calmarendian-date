# Calmarendian Date
## What is It?
**npm_calmarendian_date** is a Python package that provides a `CalmarendianDate` class for the *Calendar of Lorelei* in the same way the Python Standard Library provides a `date` class for the Gregorian Calendar.

## The Calendar of Lorelei
The planet of [Calmarendi](https://www.worldanvil.com/w/calmarendi-natasha-moorfield/a/calmarendi-article) takes, from the perspective of an observer from Earth, seven years to orbit its star. The [Calendar of Lorelei](https://www.worldanvil.com/w/calmarendi-natasha-moorfield/a/the-calendar-of-lorelei-article), which divides this orbital period into seven seasons of fifty weeks of seven days (plus a few days added on to keep everything lined up) is what Calmarendians use to keep track of time.

## Where to Get It
The source code is hosted on GitHub at:
https://github.com/natashamoorfield/npm_calmarendian_date

## Installation
Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/npm_calmarendian_date).

*We strongly recommend installing our packages in a virtual environment rather than cluttering up your system's Python installation with all this junk.*

```bash
pip install npm-calmarendian-date
```

## Usage
This simple example:
```python
from npm_calmarendian_date import CalmarendianDate

d = CalmarendianDate.from_date_string('777-7-07-7')
print(d.colloquial_date())
```
will output:
```Sunday, Week 7 of Onset 777```

*Full documentation awaited.*

## Requirements

`npm_calmarendian_date` has been tested with Python 3.8, 3.9 and 3.10.

It has no other dependencies.
