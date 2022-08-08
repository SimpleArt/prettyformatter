"""
Implements:
    PrettyClass
"""
import re
from typing import TypeVar

from ._prettyformatter import pformat

Self = TypeVar("Self", bound="PrettyClass")

# Formatting options accepted.
FSTRING_FORMATTER = re.compile(
    "(?:(?P<shorten>[TF][|])?(?:(?P<depth>[0-9]+)>>)?(?P<indent>[1-9][0-9]*):)?"
    "(?P<specifier>.*?)"
)


class PrettyClass:
    """
    Base class for implementing pretty classes.

    Defines `__format__`, `__str__`, and `__repr__` using `pformat`.

    Implement `__pformat__` for custom `pformat` behavior.

    Example
    --------
        >>> class PrettyHelloWorld(PrettyClass):
        ...     
        ...     def __pformat__(self, specifier, depth, indent, shorten):
        ...         return "Hello world! Got {specifier!r}, {depth}, {indent}, {shorten}."
        ... 
        >>> pprint(PrettyHelloWorld())
        Hello world! Got '', 0, 4, True.
        >>> f"{PrettyHelloWorld():F|5>>6:.2f}"
        Hello World! Got '.2f', 5, 6, False

    See `help(prettyformatter)` for more information.
    """

    __slots__ = ()

    def __format__(self: Self, specifier: str) -> str:
        """
        Implements the format specification for `prettyformatter`.

        See `help(prettyformatter)` for more information.
        """
        match = FSTRING_FORMATTER.fullmatch(specifier)
        if match is None:
            raise ValueError(f"Invalid format specifier: {specifier!r}")
        shorten, depth, indent, specifier = match.groups()
        kwargs = {}
        if shorten is not None:
            kwargs["shorten"] = shorten == "T"
        if depth is not None:
            kwargs["depth"] = int(depth)
        if indent is not None:
            kwargs["indent"] = int(indent)
        return pformat(self, specifier, **kwargs)

    def __str__(self: Self) -> str:
        """
        Implements the format specification for `prettyformatter` with
        default parameters.

        See `help(prettyformatter)` for more information.
        """
        return pformat(self)

    def __repr__(self: Self) -> str:
        """
        Implements the format specification for `prettyformatter` with
        default parameters.

        See `help(prettyformatter)` for more information.
        """
        return pformat(self)
