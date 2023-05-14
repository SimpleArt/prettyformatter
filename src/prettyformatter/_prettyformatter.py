"""
Implements:
    pprint
    pformat
    register
"""
import json as _json
import operator
import re
import sys
import typing
from collections import UserDict, UserList
from enum import Enum
from itertools import islice
from math import isinf, isnan
from types import FunctionType, MethodType
from typing import Any, Optional, TypeVar, Union

if sys.version_info >= (3, 7):
    from dataclasses import fields, is_dataclass

if sys.version_info >= (3, 10):
    from types import EllipsisType
elif typing.TYPE_CHECKING:
    class EllipsisType(Enum):
        Ellipsis = "..."
else:
    EllipsisType = type(...)

if sys.version_info < (3, 9):
    from typing import AbstractSet, Callable, ChainMap, Counter
    from typing import DefaultDict, Deque, Dict, Iterable, List, Mapping
    from typing import OrderedDict, Pattern, Sequence, Tuple, Type
else:
    from builtins import dict as Dict, list as List, set as AbstractSet
    from builtins import tuple as Tuple, type as Type
    from collections import ChainMap, Counter, OrderedDict
    from collections import defaultdict as DefaultDict, deque as Deque
    from collections.abc import Set as AbstractSet, Callable, Iterable
    from collections.abc import Mapping, Sequence
    from re import Pattern

T = TypeVar("T", bound=Callable[[Any, str, int, int, bool], Any])

Specifier = TypeVar("Specifier", bound=Union[
    str,
    EllipsisType,
    AbstractSet[Any],
    Dict[Any, Any],
    List[Any],
    Tuple[Any, ...],
])

Specifiers = Tuple[
    str, str, str, str,
    str, str, str, str,
]

FSTRING_FORMATTER: Pattern[str] = re.compile(
    "(?P<fill>.*?)"
    "(?P<align>[<>=^]?)"
    "(?P<sign>[+ -]?)"
    "(?P<alternate>[#]?)"
    "[0]?"
    "(?P<width>[0-9]*)"
    "(?P<group>[_,]?)"
    "(?P<precision>(?:[.][0-9]+)?)"
    "(?P<dtype>[bcdeEfFgGnosxX%]?)"
)

FORMATTERS = []

def parse_fstring(
    specifier: str,
    cache: Dict[str, Specifiers] = OrderedDict(),
) -> Optional[Specifiers]:
    if specifier == "":
        return ("",) * 8
    elif specifier not in cache:
        if len(cache) > 4:
            cache.popitem(last=False)  # type: ignore
        match = FSTRING_FORMATTER.fullmatch(specifier)
        cache[specifier] = None if match is None else (*match.groups(),)
    return cache[specifier]

def matches_repr(subcls: Type[Any], *cls: Type[Any]) -> bool:
    """Checks if the class is a subclass that has not overridden the __repr__."""
    return any(
        issubclass(subcls, c) and subcls.__repr__ is c.__repr__
        for c in cls
    )

def pprint(
    *args: Any,
    specifier: Union[
        str,
        EllipsisType,
        AbstractSet[Specifier],
        Dict[Any, Specifier],
        List[Specifier],
        Tuple[Specifier, ...],
    ] = "",
    depth: int = 0,
    indent: int = 4,
    shorten: bool = True,
    json: bool = False,
    **kwargs: Any,
) -> None:
    """
    Pretty formats an object and prints it.

    Equivalent to `print(pformat(...), ...)`.

    For the full documentation, see:
        https://simpleart.github.io/prettyformatter/

    Parameters
    -----------
        *args:
            The arguments being printed.
        specifier:
            A format specifier e.g. ".2f".

            If `...` is given, then the result is just "...".
            If `{specifier}` is given, then elements in sets are
                formatted using the specifier in the set.
            If `{key: specifier}` is given, then dictionaries which match
                the keys will distribute the specifier to the values.
                This also includes key-value based classes, such as
                dataclasses.
            If `[specifier]` is given, then elements in lists are
                formatted using the specifier in the list.
            If `(s1, s2, ...)` is given, then tuples which match the size
                of the specifier will distribute the specifier to each
                index. This also includes arg based pretty classes.

            Specifiers can additionally be nested arbitrarily, such as
                pprint(
                    data,
                    specifier={"times": [...], "profits": [".2f"]},
                )
            which will search for dictionaries that have `"times"` and
            `"profits"` as keys, replacing any lists in the times with
            `"[...]"` and formatting elements in any lists inside the
            profits with `".2f"` to display to 2 decimals.
        depth:
            The depth of the objects.
            Their first lines are not indented.
            Other lines are indented the provided depth,
            plus more as needed.
        indent:
            The indentation used.
            Specifies how much the depth increases for inner objects.
        shorten:
            Flag for if the result may be shortened if possible.
            Ignored if json=True.
        json:
            If True, turns None into "null".
        **kwargs:
            Additional arguments for printing e.g. sep or end.

    Examples
    ---------
        >>> pprint(list(range(1000)))
        [0, 1, 2, 3, 4, ..., 997, 998, 999]
        >>> pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}])
        [
            {
                0   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                1   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                2   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                3   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                4   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
            },
        ]

    Structure
    ----------
        >>> pprint([{0: {"ABC": [list(range(30))]}}]
        [
              {
                0:
                  {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
              }
            ]

        Explanation:
            [
            ^
          no indent for the first line

                  {
                    0:
                  ^^
              indent = 2

                      {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                                               ^^^
                                           shorten = True
                  }
                ]
            ^^^^
          depth = 4
    """
    try:
        depth = operator.index(depth)
    except TypeError:
        raise TypeError("pprint could not interpret depth as an integer, got " + repr(depth)) from None
    try:
        indent = operator.index(indent)
    except TypeError:
        raise TypeError("pprint could not interpret indent as an integer, got " + repr(indent)) from None
    try:
        shorten = bool(shorten)
    except TypeError:
        raise TypeError("pprint could not interpret shorten as a boolean, got " + repr(shorten)) from None
    try:
        json = bool(json)
    except TypeError:
        raise TypeError("pprint could not interpret json as a boolean, got " + repr(json)) from None
    if depth < 0:
        raise ValueError("pprint expected depth >= 0")
    if indent <= 0:
        raise ValueError("pprint expected indent > 0")
    shorten &= not json
    print(
        *[
            pformat(
                arg,
                specifier,
                depth=depth,
                indent=indent,
                shorten=shorten,
                json=json,
            )
            for arg in args
        ],
        **kwargs,
    )

def pformat(
    obj: Any,
    specifier: Union[
        str,
        EllipsisType,
        AbstractSet[Specifier],
        Dict[Any, Specifier],
        List[Specifier],
        Tuple[Specifier, ...],
    ] = "",
    *,
    depth: int = 0,
    indent: int = 4,
    shorten: bool = True,
    json: bool = False,
) -> str:
    """
    Formats an object and depths the inner contents, if any, by the
    specified amount.

    To make your classes work with `prettyformatter`,
    see `help(prettyformatter)` for more information.

    Parameters
    -----------
        obj:
            The object being formatted.
        specifier:
            A format specifier e.g. ".2f".

            If `...` is given, then the result is just "...".
            If `{specifier}` is given, then elements in sets are
                formatted using the specifier in the set.
            If `{key: specifier}` is given, then dictionaries which match
                the keys will distribute the specifier to the values.
                This also includes key-value based classes, such as
                dataclasses.
            If `[specifier]` is given, then elements in lists are
                formatted using the specifier in the list.
            If `(s1, s2, ...)` is given, then tuples which match the size
                of the specifier will distribute the specifier to each
                index. This also includes arg based pretty classes.

            Specifiers can additionally be nested arbitrarily, such as
                pprint(
                    data,
                    specifier={"times": [...], "profits": [".2f"]},
                )
            which will search for dictionaries that have `"times"` and
            `"profits"` as keys, replacing any lists in the times with
            `"[...]"` and formatting elements in any lists inside the
            profits with `".2f"` to display to 2 decimals.
        depth:
            The depth of the objects.
            Their first lines are not indented.
            Other lines are indented the provided depth,
            plus more as needed.
        indent:
            The indentation used.
            Specifies how much the depth increases for inner objects.
        shorten:
            Flag for if the result may be shortened if possible.
            Ignored if json=True.
        json:
            If True, turns None into "null".

    Returns
    --------
        formatted_string:
            A formatted string, indented as necessary.

    Examples
    ---------
        >>> pprint(list(range(1000)))
        [0, 1, 2, 3, 4, ..., 997, 998, 999]
        >>> pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}])
        [
            {
                0   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                1   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                2   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                3   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                4   : {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
            },
        ]

    Structure
    ----------
        >>> pprint([{0: {"ABC": [list(range(30))]}}]
        [
              {
                0:
                  {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
              }
            ]

        Explanation:
            [
            ^
          no indent for the first line

                  {
                    0:
                  ^^
              indent = 2

                      {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                                               ^^^
                                           shorten = True
                  }
                ]
            ^^^^
          depth = 4
    """
    try:
        depth = operator.index(depth)
    except TypeError:
        raise TypeError("pformat could not interpret depth as an integer, got " + repr(depth)) from None
    try:
        indent = operator.index(indent)
    except TypeError:
        raise TypeError("pformat could not interpret indent as an integer, got " + repr(indent)) from None
    try:
        shorten = bool(shorten)
    except TypeError:
        raise TypeError("pformat could not interpret shorten as a boolean, got " + repr(shorten)) from None
    try:
        json = bool(json)
    except TypeError:
        raise TypeError("pformat could not interpret json as a boolean, got " + repr(json)) from None
    if depth < 0:
        raise ValueError("pformat expected depth >= 0")
    if indent <= 0:
        raise ValueError("pformat expected indent > 0")
    if specifier is ...:
        return "..."
    shorten &= not json
    if obj is ...:
        return "Ellipsis"
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten, json=json)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten, json=json)
    plus_plus_indent = dict(specifier=specifier, depth=depth_plus + indent, indent=indent, shorten=shorten, json=json)
    with_indent = dict(specifier=specifier, depth=depth, indent=indent, shorten=shorten, json=json)
    cls = type(obj)
    if cls is str:
        return _json.dumps(obj)
    elif not json:
        pass
    elif obj is None:
        if isinstance(specifier, str):
            specifiers = parse_fstring(specifier)
            if specifiers is not None:
                _, align, _, _, width, _, _, _ = specifiers
                return format("null", align + width)
        return "null"
    elif type(obj) is bool:
        if isinstance(specifier, str):
            specifiers = parse_fstring(specifier)
            if specifiers is not None:
                _, align, _, _, width, _, _, _ = specifiers
                return f"{obj:{align}{width}}".lower()
        return str(obj).lower()
    elif hasattr(type(obj), "__index__"):
        obj = operator.index(obj)
        if specifier == "" or not isinstance(specifier, str):
            return repr(obj)
        specifiers = parse_fstring(specifier)
        if specifiers is None:
            return repr(obj)
        _, align, sign, _, width, _, precision, dtype = specifiers
        specifier = ""
        if align is not None:
            specifier += align
        if sign in "+ ":
            specifier += " "
        if width is not None:
            specifier += width
        if dtype is None or dtype in "bcdoxn":
            return f"{obj:{specifier}}"
        dtype = dtype.lower()
        if precision is not None and dtype in "efg%":
            specifier += precision + dtype
        if dtype == "%":
            return f"{100 * obj:{specifier}g}"
        else:
            return f"{obj:{specifier}}"
    elif hasattr(type(obj), "__float__"):
        obj = float(obj)
        if isinf(obj):
            result = "Infinity" if obj > 0 else "-Infinity"
        elif isnan(obj):
            result = "NaN"
        else:
            result = repr(obj)
        if specifier == "" or not isinstance(specifier, str):
            return result
        specifiers = parse_fstring(specifier)
        if specifiers is None:
            return result
        _, align, sign, _, width, _, precision, dtype = specifiers
        specifier = ""
        if align is not None:
            specifier += align
        if isinf(obj) or isnan(obj):
            if sign in "+ " and not obj < 0:
                result = " " + result
            if width is not None:
                specifier += width
            return f"{result:{specifier}}"
        if sign == " ":
            specifier += " "
        if width is not None:
            specifier += width
        if precision is not None:
            specifier += precision
        if dtype is None:
            return f"{obj:{specifier}}"
        dtype = dtype.lower()
        if dtype == "%":
            return f"{100 * obj:{specifier}g}"
        elif dtype == "n":
            return f"{obj:{specifier}g}"
        else:
            return f"{obj:{specifier}{dtype}}"
    elif sys.version_info >= (3, 7) and is_dataclass(cls):
        return pformat_dict(
            {f.name: getattr(obj, f.name) for f in fields(cls)},
            **with_indent,
        )
    elif issubclass(cls, Mapping):
        return pformat_dict(obj, **with_indent)
    elif issubclass(cls, Sequence):
        return "[" + pformat_collection(obj, **with_indent) + "]"
    elif issubclass(cls, Iterable):
        return "[" + pformat_collection(list(obj), **with_indent) + "]"
    if hasattr(cls, "__pformat__"):
        return cls.__pformat__(obj, specifier, depth, indent, shorten, json)
    elif matches_repr(cls, str):
        try:
            return json.dumps(obj)
        except:
            return repr(obj)
    elif matches_repr(cls, ChainMap):
        return (
            cls.__name__
            + "("
            + pformat_collection(obj.maps, **with_indent)
            + ")"
        )
    elif matches_repr(cls, Counter):
        if len(obj) == 0:
            return cls.__name__ + "()"
        return (
            cls.__name__
            + "("
            + pformat_dict(obj, **with_indent)
            + ")"
        )
    elif matches_repr(cls, OrderedDict):
        if len(obj) == 0:
            return cls.__name__ + "()"
        return (
            cls.__name__
            + "(["
            + pformat_collection(obj.items(), **with_indent)
            + "])"
        )
    elif matches_repr(cls, DefaultDict):
        return cls.__name__ + pformat(
            (obj.default_factory, dict(obj)),
            **with_indent,
        )
    elif matches_repr(cls, Deque):
        if obj.maxlen is None:
            return (
                cls.__name__
                + "("
                + pformat_collection(obj, **with_indent)
                + ")"
            )
        return cls.__name__ + pformat(
            (list(obj), obj.maxlen),
            **with_indent,
        )
    elif (
        cls is not type
        and all(
            parent is expected
            for parent, expected in zip(
                cls.mro(),
                [cls, tuple, object],
            )
        )
        and all(
            hasattr(cls, attr)
            for attr in (
                "_asdict",
                "_field_defaults",
                "_fields",
                "_make",
                "_replace",
            )
        )
    ):
        return (
            cls.__name__
            + pformat_class(
                (),
                {name: getattr(obj, name) for name in cls._fields},
                **with_indent,
            )
        )
    elif not matches_repr(cls, UserList, frozenset, list, set, tuple):
        if cls in FORMATTERS:
            return FORMATTERS[cls](
                obj,
                specifier,
                depth,
                indent,
                shorten,
                json,
            )
        for c, formatter in reversed(FORMATTERS):
            if matches_repr(cls, c):
                return formatter(
                    obj,
                    specifier,
                    depth,
                    indent,
                    shorten,
                    json,
                )
        if cls is type or cls is FunctionType:
            return obj.__qualname__
        elif cls is MethodType:
            return pformat(obj.__self__, specifier) + "." + str(obj.__name__)
        if not isinstance(specifier, str) or specifier == "":
            return repr(obj)
        try:
            return format(obj, specifier)
        except:
            return repr(obj)
    s = pformat_collection(obj, **with_indent)
    if matches_repr(cls, frozenset):
        return (
            cls.__name__
            + ("()" if len(obj) == 0 else "({" + s + "})")
        )
    elif matches_repr(cls, UserList, list):
        return "[" + s + "]"
    elif matches_repr(cls, set):
        return cls.__name__ + "()" if len(obj) == 0 else "{" + s + "}"
    elif len(obj) == 1 and not s.strip().endswith(","):
        return "(" + s + ",)"
    else:
        return "(" + s + ")"

def register(*args: Type[Any]) -> Callable[[T], T]:
    """
    Register classes with formatters. Useful for enabling pprint with
    already defined classes.

    For classes you define, it is preferable that the `PrettyClass` is
    implemented instead. See `help(prettyformatter)` for more
    information.

    Usage
    ------
        @register(cls1, cls2, ...)
        def formatter(obj, specifier, depth, indent, shorten, json):
            js = "j!" if json else "T" if shorten else "F"
            return f"{obj:{js}|{depth}>>{indent}:specifier}"

    Example
    --------
        >>> import numpy as np
        >>> 
        >>> @register(np.ndarray)
        ... def pformat_ndarray(obj, specifier, depth, indent, shorten, json):
        ...     if json:
        ...         return pformat(obj.tolist(), specifier, depth, indent, shorten, json)
        ...     with np.printoptions(formatter=dict(all=lambda x: format(x, specifier))):
        ...         return repr(obj).replace("\\n", "\\n" + " " * depth)
        ... 
        >>> pprint(dict.fromkeys("ABC", np.arange(9).reshape(3, 3)))
        {
            "A":
                array([[0, 1, 2],
                       [3, 4, 5],
                       [6, 7, 8]]),
            "B":
                array([[0, 1, 2],
                       [3, 4, 5],
                       [6, 7, 8]]),
            "C":
                array([[0, 1, 2],
                       [3, 4, 5],
                       [6, 7, 8]]),
        }
        >>> pprint(dict.fromkeys("ABC", np.arange(9).reshape(3, 3)), json=True)
        {
            "A" : [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
            "B" : [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
            "C" : [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
        }
    """
    for cls in args:
        if not isinstance(cls, type):
            raise TypeError("register expected a type for cls, got " + repr(cls))
    def decorator(func: T) -> T:
        if not callable(func):
            raise TypeError("@register expected a formatter function, got " + repr(func))
        FORMATTERS.extend((cls, func) for cls in args)
        return func
    return decorator

def align(indentations: Mapping[int, int]) -> Mapping[int, bool]:
    """
    Estimates reasonable alignments for key-value pairs by grouping
    nearby alignments to the deeper indentation.
    """
    if len(indentations) == 0:
        return {}
    L = range(min(indentations), max(indentations) + 1)
    moved = 0
    unmoved = 0
    is_moved = [False] * len(L)
    for i in reversed(range(len(L))):
        if i + 2 < len(L):
            temp = (
                unmoved
                + 5
                - 2 * indentations[L[i + 2]]
                + 4 * indentations[L[i + 1]]
                - 2 * indentations[L[i]]
            )
        elif i + 1 < len(L):
            temp = (
                unmoved
                + 2
                + 2 * indentations[L[i + 1]]
                - 2 * indentations[L[i]]
            )
        else:
            temp = unmoved
        if moved > unmoved:
            unmoved = moved
            is_moved[i + 1] = True
            if i + 2 < len(L):
                is_moved[i + 2] = False
        moved = temp
    if moved > unmoved:
        is_moved[0] = True
        if 1 < len(L):
            is_moved[1] = False
    return dict(zip(L, is_moved))

def dict_specifier(
    specifier: Dict[
        Any,
        Union[
            str,
            EllipsisType,
            AbstractSet[Specifier],
            Dict[Any, Specifier],
            List[Specifier],
            Tuple[Specifier, ...],
        ],
    ],
    key: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    try:
        kwargs["specifier"] = specifier[key]
    except (KeyError, TypeError):
        kwargs["specifier"] = specifier
    return kwargs

@register(UserDict, dict)
def pformat_dict(
    obj: Mapping[Any, Any],
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
    """Formats a mapping as a dict."""
    if isinstance(specifier, set) and len(specifier) == 1:
        for spec in specifier:
            if spec is ...:
                return "{...}"
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten, json=json)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten, json=json)
    plus_plus_indent = dict(specifier=specifier, depth=depth_plus + indent, indent=indent, shorten=shorten, json=json)
    if len(obj) < 10:
        keys = [
            pformat(key, **no_indent)
            for key in obj
        ]
        if isinstance(specifier, dict):
            values = [
                pformat(value, **dict_specifier(key=key, **no_indent))
                for key, value in obj.items()
            ]
        else:
            values = [
                pformat(value, **no_indent)
                for key, value in obj.items()
            ]
        s = ", ".join([k + ": " + v for k, v in zip(keys, values)])
        if len(s) < 50 and "\n" not in s:
            return "{" + s + "}"
    if shorten:
        key_types = {*map(type, obj)}
        if len(key_types) > 1:
            shorten = False
        elif any(issubclass(cls, str) for cls in key_types):
            pass
        elif any(issubclass(cls, Mapping) for cls in key_types):
            if len({
                frozenset(
                    (type(key), type(value))
                    for key, value in x.items()
                )
                for x in obj
            }) > 1:
                shorten = False
        elif any(issubclass(cls, Iterable) for cls in key_types):
            if len({frozenset(map(type, key)) for key in obj}) > 1:
                shorten = False
        del key_types
    if shorten:
        value_types = {*map(type, obj.values())}
        if len(value_types) > 1:
            shorten = False
        elif any(issubclass(cls, str) for cls in value_types):
            pass
        elif any(issubclass(cls, Mapping) for cls in value_types):
            if len({
                frozenset(
                    (type(key), type(value))
                    for key, value in x.items()
                )
                for x in obj.values()
            }) > 1:
                shorten = False
        elif any(issubclass(cls, Iterable) for cls in value_types):
            if len({frozenset(map(type, value)) for value in obj.values()}) > 1:
                shorten = False
        del value_types
    if len(obj) < 10 or not shorten:
        if isinstance(specifier, dict):
            content = [
                (
                    pformat(key, **plus_indent),
                    pformat(value, **dict_specifier(key=key, **plus_plus_indent)),
                )
                for key, value in obj.items()
            ]
        else:
            content = [
                (
                    pformat(key, **plus_indent),
                    pformat(value, **plus_plus_indent),
                )
                for key, value in obj.items()
            ]
    else:
        if isinstance(specifier, dict):
            content = [
                *[
                    (
                        pformat(key, **plus_indent),
                        pformat(value, **dict_specifier(key=key, **plus_plus_indent)),
                    )
                    for key, value in islice(obj.items(), 5)
                ],
                ...,
                *[
                    (
                        pformat(key, **plus_indent),
                        pformat(value, **plus_plus_indent),
                    )
                    for key, value in islice(obj.items(), len(obj) - 3, None)
                ],
            ]
        else:
            content = [
                *[
                    (
                        pformat(key, **plus_indent),
                        pformat(value, **dict_specifier(key=key, **plus_plus_indent)),
                    )
                    for key, value in islice(obj.items(), 5)
                ],
                ...,
                *[
                    (
                        pformat(key, **plus_indent),
                        pformat(value, **plus_plus_indent),
                    )
                    for key, value in islice(obj.items(), len(obj) - 3, None)
                ],
            ]
    s = ", ".join(["..." if c is ... else (c[0] + ": " + c[1]) for c in content])
    if len(s) < 100 and "\n" not in s:
        return "{" + s + "}"
    alignment = align(Counter(
        (len(c[0]) + indent - 1) // indent
        for c in content
        if c is not ...
        if len(c[0]) + len(c[1]) < 90
        if "\n" not in c[0]
        if "\n" not in c[1]
    ))
    return (
        ("{\n" + " " * depth_plus)
        + (",\n" + " " * depth_plus).join([
                "..."
                    if
                c is ...
                    else
                (
                    c[0]
                    + " " * (indent * alignment[(len(c[0]) + indent - 1) // indent])
                    + " " * (-len(c[0]) % indent)
                    + ": "
                    + c[1]
                )
                    if
                (
                    len(c[0]) + len(c[1]) < 90
                    and "\n" not in c[0]
                    and "\n" not in c[1]
                )
                    else
                (
                    c[0]
                    + ":\n"
                    + " " * (depth_plus + indent)
                    + c[1]
                )
                for c in content
            ])
        + ("," * (1 - json) + "\n" + " " * depth + "}")
    )

def pformat_collection(
    obj: Iterable[Any],
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
    """Formats as an iterable as a list without the enclosing brackets."""
    if (
        isinstance(specifier, list)
        and isinstance(obj, Sequence)
        and len(specifier) == 1
        and specifier[0] is ...
    ):
        return "..."
    elif (
        isinstance(specifier, set)
        and isinstance(obj, AbstractSet)
        and len(specifier) == 1
    ):
        for spec in specifier:
            if spec is ...:
                return "..."
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten, json=json)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten, json=json)
    if isinstance(specifier, list) and isinstance(obj, Sequence) and len(specifier) == 1:
        no_indent["specifier"] = plus_indent["specifier"] = specifier[0]
    elif isinstance(specifier, set) and isinstance(obj, AbstractSet) and len(specifier) == 1:
        for spec in specifier:
            no_indent["specifier"] = plus_indent["specifier"] = spec
    cls = type(obj)
    if len(obj) < 10:
        if isinstance(specifier, tuple) and isinstance(obj, tuple) and len(specifier) == len(obj):
            content = [
                pformat(x, **{**no_indent, "specifier": spec})
                for x, spec in zip(obj, specifier)
            ]
        else:
            content = [
                pformat(x, **no_indent)
                for x in obj
            ]
        s = ", ".join(content)
        if len(s) < 25 and "\n" not in s or len(s) < 50:
            return s
        s = (",\n" + " " * depth_plus).join([
                c.replace("\n", "\n" + " " * depth_plus)
                for c in content
            ])
        s = (
            ("\n" + " " * depth_plus)
            + s
            + ("," * (1 - json) + "\n" + " " * depth)
        )
        if max(map(len, s.splitlines())) < 50 and len(s) < 120:
            return s
    shorten &= not isinstance(obj, tuple)
    if shorten:
        types = {*map(type, obj)}
        if len(types) > 1:
            shorten = False
        elif any(issubclass(cls, str) for cls in types):
            pass
        elif any(issubclass(cls, Mapping) for cls in types):
            if len({
                frozenset(
                    (type(key), type(value))
                    for key, value in x.items()
                )
                for x in obj
            }) > 1:
                shorten = False
        elif any(issubclass(cls, Iterable) for cls in types):
            if len({frozenset(map(type, x)) for x in obj}) > 1:
                shorten = False
        del types
    if len(obj) >= 10 and shorten:
        content = [
            *[
                pformat(x, **plus_indent)
                for x in islice(obj, 5)
            ],
            "...",
            *[
                pformat(x, **plus_indent)
                for x in islice(obj, len(obj) - 3, None)
            ],
        ]
    elif isinstance(specifier, tuple) and isinstance(obj, tuple) and len(specifier) == len(obj):
        content = [
            pformat(x, **{**plus_indent, "specifier": spec})
            for x, spec in zip(obj, specifier)
        ]
    else:
        content = [
            pformat(x, **plus_indent)
            for x in obj
        ]
    s = ", ".join(content)
    if "\n" not in s and len(s) < 120:
        return s
    return (
        ("\n" + " " * depth_plus)
        + (",\n" + " " * depth_plus).join(content)
        + ("," * (1 - json) + "\n" + " " * depth)
    )

def pformat_class(
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
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
    Formats an object as "cls_name(*args, **kwargs)" without the
    "cls_name", unless `json=True` in which case the result is
    "[args, kwargs]".
    """
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten, json=json)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten, json=json)
    plus_plus_indent = dict(specifier=specifier, depth=depth_plus + indent, indent=indent, shorten=shorten, json=json)
    with_indent = dict(specifier=specifier, depth=depth, indent=indent, shorten=shorten, json=json)
    if json:
        if not isinstance(specifier, dict) or specifier.keys() != {"args", "kwargs"}:
            with_indent["specifier"] = {"args": specifier, "kwargs": specifier}
        return pformat_dict({"args": args, "kwargs": kwargs}, **with_indent)
    if isinstance(specifier, dict) and specifier.keys() == {"args", "kwargs"}:
        args_specifier = specifier["args"]
        kwargs_specifier = specifier["kwargs"]
    else:
        args_specifier = kwargs_specifier = specifier
    if len(args) + 2 * len(kwargs) < 8:
        s = "("
        no_indent["specifier"] = args_specifier
        if isinstance(args_specifier, tuple) and len(args_specifier) == len(args):
            s += ", ".join([
                pformat(x, **{**no_indent, "specifier": spec})
                for x, c in zip(args, args_specifier)
            ])
        else:
            s += ", ".join([
                pformat(x, **no_indent)
                for x in args
            ])
        if len(args) > 0 < len(kwargs):
            s += ", "
        no_indent["specifier"] = kwargs_specifier
        if isinstance(kwargs_specifier, dict):
            s += ", ".join([
                name
                + "="
                + pformat(value, **dict_specifier(key=name, **no_indent))
                for name, value in kwargs.items()
            ])
        else:
            s += ", ".join([
                name
                + "="
                + pformat(value, **no_indent)
                for name, value in kwargs.items()
            ])
        s += ")"
        no_indent["specifier"] = specifier
        if len(s) < 100 and "\n" not in s:
            return s
        del s
        kwarg_lengths = {*map(len, kwargs)}
    if (
        len(args) + 2 * len(kwargs) >= 8
        or len(kwarg_lengths) > 1
        or any(L >= indent for L in kwarg_lengths)
    ):
        no_indent["specifier"] = kwargs_specifier
        plus_indent["specifier"] = args_specifier
        plus_plus_indent["specifier"] = kwargs_specifier
        s = "(\n" + " " * depth_plus
        if isinstance(args_specifier, tuple) and len(args_specifier) == len(args):
            s += (",\n" + " " * depth_plus).join([
                pformat(x, **plus_indent)
                for x, spec in zip(args, args_specifier)
            ])
        else:
            s += (",\n" + " " * depth_plus).join([
                pformat(x, **plus_indent)
                for x in args
            ])
        if len(args) > 0 < len(kwargs):
            s += ",\n" + " " * depth_plus
        if isinstance(kwargs_specifier, dict):
            content = [
                pformat(value, **dict_specifier(key=name, **no_indent))
                for name, value in kwargs.items()
            ]
        else:
            content = [
                pformat(value, **no_indent)
                for value in kwargs.values()
            ]
        newlines = {i for i, c in enumerate(content) if "\n" in c}
        alignment = align(Counter(
            len(name) // indent
            for i, (name, c) in enumerate(zip(kwargs, content))
            if len(name) + len(c) < 90
            if i not in newlines
        ))
        for i, (name, c) in enumerate(zip(kwargs, content)):
            if i in newlines or len(name) + len(c) >= 90:
                content[i] = name + "=\n" + " " * (depth_plus + indent) + c.replace("\n", "\n" + "  " * indent)
                continue
            content[i] = (
                name
                + " " * (
                    1 + (~len(name) % indent) + indent * alignment[len(name) // indent]
                )
                + ("= " + c)
            )
        if isinstance(kwargs_specifier, dict):
            for i, (name, value) in enumerate(kwargs.items()):
                if i not in newlines or len(name) + len(c) >= 90:
                    continue
                content[i] = (
                    name
                    + "=\n"
                    + " " * (depth_plus + indent)
                    + pformat(value, **dict_specifier(key=name, **plus_plus_indent))
                )
        else:
            for i, (name, value) in enumerate(kwargs.items()):
                if i not in newlines or len(name) + len(c) >= 90:
                    continue
                content[i] = (
                    name
                    + "=\n"
                    + " " * (depth_plus + indent)
                    + pformat(value, **plus_plus_indent)
                )
        return s + (",\n" + " " * depth_plus).join(content) + (",\n" + " " * depth + ")")
    s = "(\n" + " " * depth_plus
    plus_indent["specifier"] = args_specifier
    if isinstance(args_specifier, tuple) and len(args_specifier) == len(args):
        s += (",\n" + " " * depth_plus).join([
            pformat(x, **{**plus_indent, "specifier": spec})
            for x, spec in zip(args, args_specifier)
        ])
    else:
        s += (",\n" + " " * depth_plus).join([
            pformat(x, **plus_indent)
            for x in args
        ])
    if len(args) > 0 < len(kwargs):
        s += ",\n" + " " * depth_plus
    plus_plus_indent["specifier"] = kwargs_specifier
    if isinstance(kwargs_specifier, dict):
        s += (",\n" + " " * depth_plus).join([
            name
            + "="
            + pformat(value, **dict_specifier(key=name, **plus_plus_indent))
            for name, value in kwargs.items()
        ])
    else:
        s += (",\n" + " " * depth_plus).join([
            name
            + "="
            + pformat(value, **plus_plus_indent)
            for name, value in kwargs.items()
        ])
    return s + (",\n" + " " * depth + ")")
