class CalmarendianDateError(Exception):
    """
    A generic exception to be raised when creating or processing a CalmarendianDate object.
    """
    pass


class CalmarendianDateRangeError(CalmarendianDateError):
    """
    An exception to be raised when an operation on a CalmarendianDate object results in a value
    outside permitted bounds.
    """
    pass


class CalmarendianDateDomainError(CalmarendianDateError):
    """
    An exception to be raised when an argument is passed to a CalmarendianDate method
    which is outside permitted bounds.
    """
    pass


class CalmarendianDateFormatError(CalmarendianDateError):
    """
    An exception to be raised when a date string is not in a recognized format.
    """
    pass


class CalmarendianDateValueError(CalmarendianDateError):
    """
    An exception to be raised when an argument is passed to an CalmarendianDate method
    which is inconsistent with current state.  For example: whilst week number 51 is valid
    in certain circumstances, it is not when the season is already set to 6.
    """