"""
Implements:
    PrettyClass
"""
from typing import TypeVar

from ._prettyformatter import pformat

Self = TypeVar("Self", bound="PrettyClass")


class PrettyClass:
    """
    Base class for implementing pretty classes.

    Defines `__format__`, `__str__`, and `__repr__` using `pformat`.

    Implement `__pformat__` for custom `pformat` behavior.

    For the full documentation, see:
        https://simpleart.github.io/prettyformatter/PrettyClass

    Example
    --------
        >>> class PrettyHelloWorld(PrettyClass):
        ...     
        ...     def __pformat__(self, specifier, depth, indent, shorten, json):
        ...         return f"Hello world! Got {specifier!r}, {depth}, {indent}, {shorten}, {json}."
        ... 
        >>> pprint(PrettyHelloWorld())
        Hello world! Got '', 0, 4, True, False.

    See `help(prettyformatter)` for more information.
    """

    __slots__ = ()

    def __format__(self: Self, specifier: str) -> str:
        """
        Implements the format specification for `prettyformatter`.

        See `help(prettyformatter)` for more information.
        """
        return pformat(self, specifier)

    def __pformat__(self: Self, specifier: str, depth: int, indent: int, shorten: bool, json: bool) -> str:
        """
        Default implementation does nothing.
        """
        formatter = super(PrettyClass, type(self)).__format__
        if formatter is not object.__format__:
            return formatter(self, specifier)
        else:
            return super(PrettyClass, type(self)).__repr__(self)

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
