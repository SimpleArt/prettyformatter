"""
Implements:
    PrettyClass
"""
import sys
from typing import Any, TypeVar, Union

if sys.version_info < (3, 9):
    from typing import AbstractSet, Dict, List, Tuple
else:
    from builtins import dict as Dict, list as List, tuple as Tuple
    from collections.abc import Set as AbstractSet

from ._prettyformatter import EllipsisType, Specifier, pformat, pformat_class

Self = TypeVar("Self", bound="PrettyClass")


class PrettyClass:
    """
    Base class for implementing pretty classes.

    Defines `__format__`, `__str__`, and `__repr__` using `pformat`.

    For the full documentation, see:
        https://simpleart.github.io/prettyformatter/PrettyClass

    Dunders
    ---------

    Implement `__pargs__` and/or `__pkwargs__` if the desired `pformat` is
    `cls_name(*args, **kwargs)`.
        >>> class Dog(PrettyClass):
        ...     
        ...     def __init__(self, name, **kwargs):
        ...         self.name = name
        ...         self.attributes = kwargs
        ...     
        ...     def __pargs__(self):
        ...         return (self.name,)
        ...     
        ...     def __pkwargs__(self):
        ...         return self.attributes
        ... 
        >>> Dog("Fido", age=3)
        Dog("Fido", age=3)

    Implement `__pformat__` for more customized `pformat` behavior.
        >>> class PrettyHelloWorld(PrettyClass):
        ...     
        ...     def __pformat__(self, specifier, depth, indent, shorten, json):
        ...         return f"Hello world! Got {specifier!r}, {depth}, {indent}, {shorten}, {json}."
        ... 
        >>> pprint(PrettyHelloWorld())
        Hello world! Got '', 0, 4, True, False.

    JSON serialization
    --------------------

    If the default `__pformat__` is used and `__pargs__` and/or
    `__pkwargs__` is implemented, then JSON serialization is done by
    converting the `args` into a `list` and the `kwargs` into a `dict`.
    If both are given, they are combined using the format of
    `{"class": cls_name, "args": list(args), "kwargs": kwargs}`.

        >>> pprint(Dog("Fido", age=3), json=True)
        {"class": "Dog", "args": ["Fido"], "kwargs": {"age": 3}}
    """

    __slots__ = ()

    def __format__(self: Self, specifier: str) -> str:
        """
        Implements the format specification for `prettyformatter`.
        """
        return pformat(self, specifier)

    def __pargs__(self: Self) -> Tuple[Any, ...]:
        """
        Defines the positional arguments for "cls_name(*args, **kwargs)".
        Raises NotImplementedError, by default, if there are no args.
        """
        raise NotImplementedError

    def __pformat__(
        self: Self,
        specifier: Union[
            str,
            EllipsisType,
            AbstractSet[Specifier],
            Dict[Any, Specifier],
            List[Specifier],
            Tuple[Specifier, ...],
        ],
        depth: int,
        indent: int,
        shorten: bool,
        json: bool,
    ) -> str:
        """
        Default implementation uses __pargs__ and __pkwargs__.
        """
        cls = type(self)
        try:
            args = cls.__pargs__(self)
        except NotImplementedError:
            args = None
        else:
            if not isinstance(args, tuple):
                raise TypeError("__pargs__ expected a tuple, got " + repr(args))
        try:
            kwargs = cls.__pkwargs__(self)
        except NotImplementedError:
            kwargs = None
        else:
            if not isinstance(kwargs, dict):
                raise TypeError("__pkwargs__ expected a dict, got " + repr(kwargs))
            for name in kwargs:
                if not isinstance(name, str):
                    raise TypeError("__pkwargs__ expected a dict of 'name': value pairs, got " + repr(name))
        with_indent = dict(specifier=specifier, depth=depth, indent=indent, shorten=shorten, json=json)
        if args is None is kwargs:
            formatter = super(PrettyClass, cls).__format__
            if formatter is not object.__format__:
                return formatter(self, specifier)
            else:
                return super().__repr__()
        elif json:
            if args is None:
                return pformat(kwargs, **with_indent)
            elif kwargs is None:
                return pformat(args, **with_indent)
            else:
                return pformat(
                    {
                        "class": cls.__name__,
                        "args": args,
                        "kwargs": kwargs,
                    },
                    **with_indent,
                )
        elif args is None:
            args = ()
        elif kwargs is None:
            kwargs = {}
        return cls.__name__ + pformat_class(args, kwargs, **with_indent)

    def __pkwargs__(self: Self) -> Dict[str, Any]:
        """
        Defines the keyword arguments for "cls_name(*args, **kwargs)".
        Raises NotImplementedError, by default, if there are no kwargs.
        """
        raise NotImplementedError

    def __str__(self: Self) -> str:
        """
        Implements the format specification for `prettyformatter` with
        default parameters.
        """
        return pformat(self)

    def __repr__(self: Self) -> str:
        """
        Implements the format specification for `prettyformatter` with
        default parameters.
        """
        return pformat(self)
