"""
Implements:
    pprint
    pformat
    register
"""
import operator
import re
from collections import ChainMap, Counter, OrderedDict, UserDict
from collections import UserList, defaultdict, deque
from dataclasses import fields, is_dataclass
from itertools import islice
from typing import Any, Callable, Collection, List, Mapping, Tuple, Type, TypeVar, Union

T = TypeVar("T")
Formatter = Callable[[T, str, int, int, bool], str]
Self = TypeVar("Self", bound="PrettyDataclass")

FORMATTERS: List[Tuple[Type[Any], Callable[[Any], str]]] = []

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

    To make your classes work with `prettyformatter`,
    see `help(prettyformatter)` for more information.

    Parameters
    -----------
        *args:
            The arguments being printed.
        specifier:
            A format specifier e.g. ".2f".
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

    Structure
    ----------
        >>> pprint([{0: {"ABC": [list(range(30))]}}]
        [
              {
                0:
                  {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
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

                      {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                                               ^^^
                                           shorten = True
                  }
                ]
            ^^^^
          depth = 4
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

    To make your classes work with `prettyformatter`,
    see `help(prettyformatter)` for more information.

    Parameters
    -----------
        obj:
            The object being formatted.
        specifier:
            A format specifier e.g. ".2f".
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

    Structure
    ----------
        >>> pprint([{0: {"ABC": [list(range(30))]}}]
        [
              {
                0:
                  {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
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

                      {'ABC': [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
                                               ^^^
                                           shorten = True
                  }
                ]
            ^^^^
          depth = 4
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
    if hasattr(cls, "__pformat__"):
        return cls.__pformat__(obj, specifier, depth, indent, shorten)
    elif matches_repr(cls, str):
        return repr(f"{obj:{specifier}}")
    elif matches_repr(cls, ChainMap):
        return f"{cls.__name__}({pformat(obj.maps, **with_indent)[1:-1]})"
    elif matches_repr(cls, Counter):
        if len(obj) == 0:
            return f"{cls.__name__}()"
        return f"{cls.__name__}({pformat_dict(obj, **with_indent)})"
    elif matches_repr(cls, OrderedDict):
        if len(obj) == 0:
            return f"{cls.__name__}()"
        return f"{cls.__name__}([{pformat_collection(obj.items(), **with_indent)}])"
    elif matches_repr(cls, defaultdict):
        return f"{cls.__name__}{pformat((obj.default_factory, dict(obj)), **with_indent)}"
    elif matches_repr(cls, deque):
        if obj.maxlen is None:
            return f"{cls.__name__}({pformat_collection(obj, **with_indent)})"
        return f"{cls.__name__}{pformat((list(obj), obj.maxlen), **with_indent)}"
    elif (
        all(
            parent is expected
            for parent, expected in zip(cls.mro(), [cls, tuple, object])
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
        if len(cls._fields) > 3:
            return (
                (f"{cls.__name__}(\n" + " " * depth_plus)
                + (",\n" + " " * depth_plus).join([
                        f"{name}=\n    "
                        + " " * depth_plus
                        + pformat(getattr(obj, name), **plus_plus_indent)
                        for name in cls._fields
                    ])
                + (",\n" + " " * depth + ")")
            )
        s = (
            f"{cls.__name__}("
            + ", ".join([
                    f"{name}={pformat(getattr(obj, name), **no_indent)}"
                    for name in cls._fields
                ])
            + ")"
        )
        if len(s) < 25 and "\n" not in s or len(s) < 50:
            if "\n" not in s:
                return s
            return (
                (f"{cls.__name__}(\n" + " " * depth_plus)
                + (",\n" + " " * depth_plus).join([
                        f"{name}="
                        + pformat(getattr(obj, name), **no_indent).replace("\n", "\n    " + " " * depth_plus)
                        for name in cls._fields
                    ])
                + (",\n" + " " * depth + ")")
            )
        if len({len(name) for name in cls._fields}) > 1:
            return (
                (f"{cls.__name__}(\n" + " " * depth_plus)
                + (",\n" + " " * depth_plus).join([
                        f"{name}=\n    "
                        + " " * depth_plus
                        + pformat(getattr(obj, name), **plus_plus_indent)
                        for name in cls._fields
                    ])
                + (",\n" + " " * depth + ")")
            )
        return (
            (f"{cls.__name__}(\n" + " " * depth_plus)
            + (",\n" + " " * depth_plus).join([
                    f"{name}="
                    + pformat(getattr(obj, name), **plus_plus_indent)
                    for name in cls._fields
                ])
            + (",\n" + " " * depth + ")")
        )
    elif not matches_repr(cls, UserList, frozenset, list, set, tuple):
        for c, formatter in reversed(FORMATTERS):
            if matches_repr(cls, c):
                return formatter(obj, specifier, depth, indent, shorten)
        try:
            return f"{obj:{'FT'[shorten]}|{depth}>>{indent}:{specifier}}"
        except (TypeError, ValueError):
            return f"{obj:{specifier}}"
    s = pformat_collection(obj, specifier, depth, indent, shorten)
    if matches_repr(cls, frozenset):
        return f"{cls.__name__}()" if len(obj) == 0 else f"{cls.__name__}({{{s}}})"
    elif matches_repr(cls, UserList, list):
        return f"[{s}]"
    elif matches_repr(cls, set):
        return f"{cls.__name__}()" if len(obj) == 0 else f"{{{s}}}"
    elif len(obj) == 1 and not s.strip().endswith(","):
        return f"({s},)"
    else:
        return f"({s})"

def register(*args: Type[T]) -> Callable[[Formatter[T]], Formatter[T]]:
    """
    Register classes with formatters. Useful for enabling pprint with
    already defined classes.

    For classes you define, it is preferable that the `PrettyClass` is
    implemented instead. See `help(prettyformatter)` for more
    information.

    Usage
    ------
        @register(cls1, cls2, ...)
        def formatter(obj, specifier, depth, indent, shorten):
            return f"{obj:{shorten}|{depth}>>{indent}:specifier}"

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
        FORMATTERS.extend((cls, func) for cls in args)
        return func
    return decorator

@register(UserDict, dict)
def pformat_dict(obj: Mapping[Any, Any], specifier: str, depth: int, indent: int, shorten: bool) -> str:
    """Formats a mapping as a dict."""
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten)
    plus_plus_indent = dict(specifier=specifier, depth=depth_plus + indent, indent=indent, shorten=shorten)
    if len(obj) < 10:
        s = ", ".join([
                f"{pformat(key, **no_indent)}: {pformat(value, **no_indent)}"
                for key, value in obj.items()
            ])
        if len(s) < 25 and "\n" not in s or len(s) < 50:
            if "\n" not in s:
                return f"{{{s}}}"
            s = (
                ("{\n" + " " * depth_plus)
                + ",\n".join([
                        f"{pformat(key, **no_indent)}: {pformat(value, **no_indent)}"
                        for key, value in obj.items()
                    ]).replace("\n", "\n" + " " * depth_plus)
                + ("\n" + " " * depth + "}")
            )
            if max(map(len, s.splitlines())) < 50 and len(s) < 120:
                return s
    if len(obj) < 10 or not shorten:
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
            ...,
            *[
                (pformat(key, **plus_indent), pformat(value, **plus_plus_indent))
                for key, value in islice(obj.items(), len(obj) - 3, None)
            ],
        ]
    s = ", ".join(["..." if c is ... else f"{c[0]}: {c[1]}" for c in content])
    if len(s) < 50 and "\n" not in s:
        return f"{{{s}}}"
    return (
        ("{\n" + " " * depth_plus)
        + (",\n" + " " * depth_plus).join([
                "..."
                if c is ...
                else c[0] + ":\n" + " " * (depth_plus + indent) + c[1]
                for c in content
            ])
        + (",\n" + " " * depth + "}")
    )

def pformat_collection(obj: Collection[Any], specifier: str, depth: int, indent: int, shorten: bool) -> str:
    """Formats as an collection as a list without the enclosing brackets."""
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten)
    cls = type(obj)
    if len(obj) < 10:
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
        s = "\n" + " " * depth_plus + f"{s},\n" + " " * depth
        if max(map(len, s.splitlines())) < 50 and len(s) < 120:
            return s
    if len(obj) < 10 or not shorten:
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
        return s
    return (
        ("\n" + " " * depth_plus)
        + (",\n" + " " * depth_plus).join(content)
        + (",\n" + " " * depth)
    )
