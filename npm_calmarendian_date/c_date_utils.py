"""
Common utility functions used in various parts of the library.
"""
import math
from typing import Union, Tuple

RealNumber = Union[int, float]


def split_float(x: RealNumber) -> Tuple[int, float]:
    """
    Wrapper function for the standard math.modf() method.

    Returns the integer and fractional parts of the argument as a two-tuple but, more intuitively, with
    the integer part first, converted to an integer type. Within the context of the CalmarendianTimeDelta class
    we always need the whole part specifically to be an integer, not a float.
    """
    fractional_part, whole_part = math.modf(x)
    return int(whole_part), fractional_part

