import operator
import re
from collections import ChainMap, Counter, OrderedDict, UserDict
from collections import UserList, defaultdict, deque
from collections import _tuplegetter as tuplegetter
from dataclasses import fields, is_dataclass
from itertools import islice
from typing import Any, Callable, Dict, Type, TypeVar, Union

T = TypeVar("T")
Formatter = Callable[[T, str, int, int, bool], str]
Self = TypeVar("Self", bound="PrettyDataclass")

FORMATTERS: Dict[Type[Any], Callable[[Any], str]] = {}

# Formatting options accepted.
DATACLASS_FSTRING_FORMATTER = re.compile(
    "(?:(?P<shorten>[TF][|])?(?:(?P<depth>[0-9]+)>>)?(?P<indent>[1-9][0-9]*):)?"
    "(?P<fill>.*?)"
    "(?P<align>[<>=^]?)"
    "(?P<sign>[+ -]?)"
    "(?P<alternate>[#]?)"
    "[0]?"
    "(?P<width>[0-9]*)"
    "(?P<group>[_,]?)"
    "(?P<precision>(?:.[0-9]+)?)"
    "(?P<dtype>[bcdeEfFgGnosxX%]?)"
)

def matches_repr(subcls: Type[Any], *cls: Type[Any]) -> bool:
    """Checks if the class is a subclass that has not overridden the __repr__."""
    return any(
        issubclass(subcls, c) and subcls.__repr__ is c.__repr__
        for c in cls
    )

def pprint(*args: Any, specifier: str = "", depth: int = 0, indent: int = 4, shorten: bool = True, **kwargs: Any) -> None:
    """
    Pretty formats an object and prints it.

    Equivalent to `print(pformat(...), ...)`.

    Parameters
    -----------
        *args:
            The arguments being printed.
        specifier:
            A format specifier e.g. `\".2f\"`.
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
        **kwargs:
            Additional arguments for printing e.g. sep or end.

    Examples
    ---------
        >>> pprint(list(range(1000)))
        [0, 1, 2, 3, 4, ..., 997, 998, 999]
        >>> pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}])
        [
            {
                0:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                1:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                2:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                3:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                4:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
            },
        ]

    To customize the formatting of a class, use either the
    `PrettyDataclass` to get pre-built formatting functionality,
    implement the `__format__` method to support f-strings and
    `prettyformatter` features, or use the `@register` function to
    register an already existing class to support the `pformat`
    parameters. F-strings use the indentable extended formatting
    language:

        format_spec ::= [[depth>>]indent:][rest]
        depth       ::= digit+
        indent      ::= digit+ without leading 0
        rest        ::= anything else you want to support e.g. `\".2f\"`

    For example, `f\"{custom_object:0>>8:}\"` should be supported to
    benefit from `pformat(custom_object, depth=0, indent=8)`.
    """
    if type(specifier) is not str:
        raise TypeError(f"pprint specifier expected a string, got {specifier!r}")
    try:
        depth = operator.index(depth)
    except TypeError:
        raise TypeError(f"pprint could not interpret depth as an integer, got {depth!r}") from None
    try:
        indent = operator.index(indent)
    except TypeError:
        raise TypeError(f"pprint could not interpret indent as an integer, got {indent!r}") from None
    try:
        shorten = bool(shorten)
    except TypeError:
        raise TypeError(f"pprint could not interpret shorten as a boolean, got {shorten!r}") from None
    if depth < 0:
        raise ValueError("pprint expected depth >= 0")
    if indent <= 0:
        raise ValueError("pprint expected indent > 0")
    print(*[pformat(arg, specifier, depth=depth, indent=indent, shorten=shorten) for arg in args], **kwargs)

def pformat(obj: Any, specifier: str = "", *, depth: int = 0, indent: int = 4, shorten: bool = True) -> str:
    """
    Formats an object and depths the inner contents, if any, by the
    specified amount.

    Parameters
    -----------
        obj:
            The object being formatted.
        specifier:
            A format specifier e.g. `\".2f\"`.
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

    Returns
    --------
        formatted_string:
            A formatted string, indented as necessary.

    Examples
    ---------
        >>> print(pformat(list(range(1000))))
        [0, 1, 2, 3, 4, ..., 997, 998, 999]
        >>> print(pformat([{i: {"ABC": [list(range(30))]} for i in range(5)}]))
        [
            {
                0:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                1:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                2:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                3:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                4:
                    {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
            },
        ]

    To customize the formatting of a class, use either the
    `PrettyDataclass` to get pre-built formatting functionality,
    implement the `__format__` method to support f-strings and
    `prettyformatter` features, or use the `@register` function to
    register an already existing class to support the `pformat`
    parameters. F-strings use the indentable extended formatting
    language:

        format_spec ::= [[shorten|][depth>>]indent:][rest]
        shorten     ::= T or F
        depth       ::= digit+
        indent      ::= digit+ without leading 0
        rest        ::= anything else you want to support e.g. `\".2f\"`

    For example, `f\"{custom_object:T|0>>8:}\"` should be supported to
    benefit from `pformat(custom_object, depth=0, indent=8, shorten=True)`.
    """
    if obj is ...:
        return "Ellipsis"
    if type(specifier) is not str:
        raise TypeError(f"pprint specifier expected a string, got {specifier!r}")
    try:
        depth = operator.index(depth)
    except TypeError:
        raise TypeError(f"pprint could not interpret depth as an integer, got {depth!r}") from None
    try:
        indent = operator.index(indent)
    except TypeError:
        raise TypeError(f"pprint could not interpret indent as an integer, got {indent!r}") from None
    try:
        shorten = bool(shorten)
    except TypeError:
        raise TypeError(f"pprint could not interpret shorten as a boolean, got {shorten!r}") from None
    if depth < 0:
        raise ValueError("pprint expected depth >= 0")
    if indent <= 0:
        raise ValueError("pprint expected indent > 0")
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten)
    plus_plus_indent = dict(specifier=specifier, depth=depth_plus + indent, indent=indent, shorten=shorten)
    with_indent = dict(specifier=specifier, depth=depth, indent=indent, shorten=shorten)
    cls = type(obj)
    if (
        is_dataclass(cls)
        and matches_repr(cls, PrettyDataclass)
        and cls.__format__ is PrettyDataclass.__format__
    ):
        return f"{obj:{'FT'[shorten]}|{depth}>>{indent}:{specifier}}"
    elif matches_repr(cls, str):
        return repr(f"{obj:{specifier}}")
    elif matches_repr(cls, ChainMap):
        return f"{cls.__name__}({pformat(obj.maps, **with_indent)[1:-1]})"
    elif matches_repr(cls, Counter):
        if len(obj) == 0:
            return f"{cls.__name__}()"
        return f"{cls.__name__}({pformat(dict(obj), **with_indent)})"
    elif matches_repr(cls, OrderedDict):
        if len(obj) == 0:
            return f"{cls.__name__}()"
        return f"{cls.__name__}({pformat(list(obj.items()), **with_indent)})"
    elif matches_repr(cls, defaultdict):
        return f"{cls.__name__}{pformat((obj.default_factory, dict(obj)), **with_indent)}"
    elif matches_repr(cls, deque):
        if obj.maxlen is None:
            return f"{cls.__name__}({pformat(list(obj), **with_indent)})"
        return f"{cls.__name__}{pformat((list(obj), obj.maxlen), **with_indent)}"
    elif (
        cls.mro()[1:] == [tuple, object]
        and all(
            hasattr(cls, attr)
            for attr in ("_asdict", "_field_defaults", "_fields", "_make", "_replace")
        )
        and all(
            type(f) is str and type(getattr(cls, f, None)) is tuplegetter
            for f in cls._fields
        )
    ):
        s = repr(obj)
        if len(s) < 120:
            return s
        s = f"{cls.__name__}(\n" + " " * depth_plus + (",\n" + " " * depth_plus).join([
            f"{name}={pformat(getattr(obj, name), **no_indent)}"
            for name in cls._fields
        ]) + ",\n" + " " * depth + ")"
        if max(map(len, s.splitlines())) < 120:
            return s
        return f"{cls.__name__}(\n" + " " * depth_plus + (",\n" + " " * depth_plus).join([
            f"{name}={pformat(getattr(obj, name), **plus_indent)}"
            for name in cls._fields
        ]) + ",\n" + " " * depth + ")"
    elif not matches_repr(cls, UserList, frozenset, list, set, tuple):
        for c, formatter in FORMATTERS.items():
            if matches_repr(cls, c):
                return formatter(obj, specifier, depth, indent, shorten)
        try:
            return f"{obj:{'FT'[shorten]}|{depth}>>{indent}:{specifier}}"
        except (TypeError, ValueError):
            pass
        return f"{obj:{specifier}}"
    content = [
        pformat(x, **no_indent)
        for x in obj
    ]
    s = ", ".join(content)
    if len(s) < 50 and "\n" not in s or len(s) < 120 and len(obj) < 10:
        if matches_repr(cls, frozenset):
            return "{cls.__name__}()" if len(obj) == 0 else f"{cls.__name__}({{{s}}})"
        elif matches_repr(cls, UserList, list):
            return f"[{s}]"
        elif matches_repr(cls, set):
            return "set()" if len(obj) == 0 else f"{{{s}}}"
        elif len(obj) == 1:
            return f"({s},)"
        else:
            return f"({s})"
    s = (",\n" + " " * depth_plus).join([
        c.replace("\n", "\n" + " " * depth_plus)
        for c in content
    ])
    s = "\n" + " " * depth_plus + f"{s},\n" + " " * depth
    if len(obj) < 10 and max(map(len, s.splitlines())) < 50 and len(s) < 120:
        if matches_repr(cls, frozenset):
            return f"{cls.__name__}({{{s}}})"
        elif matches_repr(cls, UserList, list):
            return f"[{s}]"
        elif matches_repr(cls, set):
            return f"{{{s}}}"
        elif len(obj) == 1:
            return f"({s},)"
        else:
            return f"({s})"
    if len(obj) < 10 or len(s) < 120 or not shorten:
        content = [pformat(x, **plus_indent) for x in obj]
    else:
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
    s = ", ".join(content)
    if "\n" not in s and len(s) < 120:
        if matches_repr(cls, frozenset):
            return f"{cls.__name__}({{{s}}})"
        elif matches_repr(cls, UserList, list):
            return f"[{s}]"
        elif matches_repr(cls, set):
            return f"{{{s}}}"
        else:
            return f"({s})"
    s = (
        "\n"
        + " " * depth_plus
        + (",\n" + " " * depth_plus).join(content)
        + ",\n"
        + " " * depth
    )
    if matches_repr(cls, frozenset):
        return f"{cls.__name__}({{{s}}})"
    elif matches_repr(cls, UserList, list):
        return f"[{s}]"
    elif matches_repr(cls, set):
        return f"{{{s}}}"
    else:
        return f"({s})"

def register(*args: Type[T]) -> Callable[[Formatter[T]], Formatter[T]]:
    """
    Register classes with formatters. Useful for enabling pprint with
    already defined classes.

    Usage
    ------
        @register(cls1, cls2, ...)
        def formatter(obj, specifier, depth, indent):
            return f"{obj:{depth}>>{indent}:specifier}"

    Example
    --------
        >>> import numpy as np
        >>> 
        >>> @register(np.ndarray)
        ... def pformat_ndarray(obj, specifier, depth, indent, shorten):
        ...     with np.printoptions(formatter=dict(all=lambda x: format(x, specifier))):
        ...         return repr(obj).replace(\"\\n\", \"\\n\" + \" \" * depth)
        ... 
        >>> pprint(dict.fromkeys("ABC", np.arange(9).reshape(3, 3)))
        {
            'A':
                array([[0, 1, 2],
                       [3, 4, 5],
                       [6, 7, 8]]),
            'B':
                array([[0, 1, 2],
                       [3, 4, 5],
                       [6, 7, 8]]),
            'C':
                array([[0, 1, 2],
                       [3, 4, 5],
                       [6, 7, 8]]),
        }
    """
    for cls in args:
        if not isinstance(cls, type):
            raise TypeError(f"register expected a type for cls, got {cls!r}")
    def decorator(func: Formatter[T]) -> Formatter[T]:
        if not callable(func):
            raise TypeError(f"@register expected a formatter function, got {func!r}")
        for cls in args:
            FORMATTERS[cls] = func
        return func
    return decorator

@register(UserDict, dict)
def pformat_dict(obj: Union[UserDict, dict], specifier: str, depth: int, indent: int, shorten: bool) -> str:
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten)
    plus_plus_indent = dict(specifier=specifier, depth=depth_plus + indent, indent=indent, shorten=shorten)
    with_indent = dict(specifier=specifier, depth=depth, indent=indent, shorten=shorten)
    s = ", ".join([
        f"{pformat(key, **no_indent)}: {pformat(value, **no_indent)}"
        for key, value in obj.items()
    ])
    if len(s) < 50 and "\n" not in s or len(s) < 120 and len(obj) < 10:
        if "\n" not in s:
            return f"{{{s}}}"
        s = (",\n").join([
            f"{pformat(key, **no_indent)}: {pformat(value, **no_indent)}"
            for key, value in obj.items()
        ])
        s = "\n" + " " * depth_plus + s.replace("\n", "\n" + " " * depth_plus) + "\n" + " " * depth
        return f"{{{s}}}"
    if len(obj) < 10 or len(s) < 120 or not shorten:
        content = [
            (pformat(key, **plus_indent), pformat(value, **plus_plus_indent))
            for key, value in obj.items()
        ]
    else:
        content = [
            *[
                (pformat(key, **plus_indent), pformat(value, **plus_plus_indent))
                for key, value in islice(obj.items(), 5)
            ],
            "...",
            *[
                (pformat(key, **plus_indent), pformat(value, **plus_plus_indent))
                for key, value in islice(obj.items(), len(obj) - 3, None)
            ],
        ]
    s = ", ".join([c if c == "..." else f"{c[0]}: {c[1]}" for c in content])
    if len(s) < 120 and "\n" not in s:
        return f"{{{s}}}"
    s = (",\n" + " " * depth_plus).join([
        c
        if c == "..."
        else c[0] + ":\n" + " " * (depth_plus + indent) + c[1]
        for c in content
    ])
    s = "\n" + " " * depth_plus + f"{s},\n" + " " * depth
    return f"{{{s}}}"


class PrettyDataclass:
    """
    Base class for creating pretty dataclasses.

    Examples:
        >>> from dataclasses import dataclass
        >>> from typing import List
        >>> 
        >>> bit_data = list(range(1000))
        >>> 
        >>> @dataclass
        ... class Data(PrettyDataclass):
        ...     data: List[int]
        ... 
        >>> Data(big_data)
        Data(data=[0, 1, 2, 3, 4, ..., 997, 998, 999])
        >>> 
        >>> @dataclass
        ... class MultiData(PrettyDataclass):
        ...     x: List[int]
        ...     y: List[int]
        ...     z: List[int]
        ... 
        >>> MultiData(big_data, big_data, big_data)
        MultiData(
            x=[0, 1, 2, 3, 4, ..., 997, 998, 999],
            y=[0, 1, 2, 3, 4, ..., 997, 998, 999],
            z=[0, 1, 2, 3, 4, ..., 997, 998, 999],
        )
    """

    __slots__ = ()

    def __init_subclass__(cls: Type[Self], **kwargs: Any) -> None:
        # Save the __repr__ directly onto the subclass so that
        # @dataclass will actually notice it.
        cls.__repr__ = cls.__repr__
        return super().__init_subclass__(**kwargs)

    def __format__(self: Self, specifier: str) -> str:
        cls = type(self)
        if not is_dataclass(cls):
            return super().__format__(specifier)
        match = DATACLASS_FSTRING_FORMATTER.fullmatch(specifier)
        if match is None:
            raise ValueError(f"Invalid format specifier: {specifier!r}")
        shorten, depth, indent, fill, align, sign, alternate, width, group, precision, dtype = match.groups()
        shorten = not (None is not shorten != "T")
        depth = 0 if depth is None else int(depth)
        indent = 4 if indent is None else int(indent)
        depth_plus = depth + indent
        attributes = [
            getattr(self, f.name)
            for f in fields(cls)
        ]
        specifier = f"{fill}{align}{sign}{alternate}{width}{group}{precision}{dtype}"
        s = (
            f"{cls.__name__}("
            + ", ".join([
                f"{f.name}={pformat(attr, specifier, depth=0, indent=indent, shorten=shorten)}"
                for f, attr in zip(fields(cls), attributes)
            ])
            + ")"
        )
        if len(s) < 120:
            return s
        return (
            f"{cls.__name__}(\n"
            + " " * depth_plus
            + (",\n" + " " * depth_plus).join([
                f"{f.name}={pformat(attr, specifier, depth=depth_plus + indent, indent=indent, shorten=shorten)}"
                for f, attr in zip(fields(cls), attributes)
            ])
            + ",\n"
            + " " * depth
            + ")"
        )

    def __repr__(self: Self) -> str:
        if is_dataclass(type(self)) and type(self).__format__ is PrettyDataclass.__format__:
            return f"{self:0>>4:}"
        else:
            return super().__repr__()
