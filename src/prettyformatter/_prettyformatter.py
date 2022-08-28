"""
Implements:
    pprint
    pformat
    register
"""
import json as _json
import operator
import re
from collections import ChainMap, Counter, OrderedDict, UserDict
from collections import UserList, defaultdict, deque
from dataclasses import fields, is_dataclass
from itertools import islice
from typing import Any, Callable, Collection, Iterable, List, Mapping, Tuple, Type, TypeVar, Union

T = TypeVar("T")
Formatter = Callable[[T, str, int, int, bool], str]

FORMATTERS: List[Tuple[Type[Any], Callable[[Any], str]]] = []

def matches_repr(subcls: Type[Any], *cls: Type[Any]) -> bool:
    """Checks if the class is a subclass that has not overridden the __repr__."""
    return any(
        issubclass(subcls, c) and subcls.__repr__ is c.__repr__
        for c in cls
    )

def pprint(*args: Any, specifier: str = "", depth: int = 0, indent: int = 4, shorten: bool = True, json: bool = False, **kwargs: Any) -> None:
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
    try:
        json = bool(json)
    except TypeError:
        raise TypeError(f"pprint could not interpret json as a boolean, got {json!r}") from None
    if depth < 0:
        raise ValueError("pprint expected depth >= 0")
    if indent <= 0:
        raise ValueError("pprint expected indent > 0")
    shorten &= not json
    print(*[pformat(arg, specifier, depth=depth, indent=indent, shorten=shorten, json=json) for arg in args], **kwargs)

def pformat(obj: Any, specifier: str = "", *, depth: int = 0, indent: int = 4, shorten: bool = True, json: bool = False) -> str:
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
    if type(specifier) is not str:
        raise TypeError(f"pformat specifier expected a string, got {specifier!r}")
    try:
        depth = operator.index(depth)
    except TypeError:
        raise TypeError(f"pformat could not interpret depth as an integer, got {depth!r}") from None
    try:
        indent = operator.index(indent)
    except TypeError:
        raise TypeError(f"pformat could not interpret indent as an integer, got {indent!r}") from None
    try:
        shorten = bool(shorten)
    except TypeError:
        raise TypeError(f"pformat could not interpret shorten as a boolean, got {shorten!r}") from None
    try:
        json = bool(json)
    except TypeError:
        raise TypeError(f"pformat could not interpret json as a boolean, got {json!r}") from None
    if depth < 0:
        raise ValueError("pformat expected depth >= 0")
    if indent <= 0:
        raise ValueError("pformat expected indent > 0")
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
        return "null"
    elif type(obj) is bool:
        return str(obj).lower()
    elif is_dataclass(cls):
        return pformat_dict({f.name: getattr(obj, f.name) for f in fields(cls)}, **with_indent)
    elif issubclass(cls, Mapping):
        return pformat_dict(obj, **with_indent)
    elif issubclass(cls, Collection):
        return f"[{pformat_collection(obj, **with_indent)}]"
    elif issubclass(cls, Iterable):
        return f"[{pformat_collection(list(obj), **with_indent)}]"
    if hasattr(cls, "__pformat__"):
        return cls.__pformat__(obj, specifier, depth, indent, shorten, json)
    elif matches_repr(cls, str):
        return repr(obj)
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
                        f"{name}=\n"
                        + " " * (depth_plus + indent)
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
                        + pformat(getattr(obj, name), **no_indent).replace("\n", "\n" + " " * (depth_plus + indent))
                        for name in cls._fields
                    ])
                + (",\n" + " " * depth + ")")
            )
        field_lengths = {len(f.name) for f in cls._fields}
        if len(field_lengths) > 1 or {1, 2, 3}.isdisjoint(field_lengths):
            return (
                (f"{cls.__name__}(\n" + " " * depth_plus)
                + (",\n" + " " * depth_plus).join([
                        f"{name}=\n"
                        + " " * (depth_plus + indent)
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
                return formatter(obj, specifier, depth, indent, shorten, json)
        try:
            return f"{obj:{specifier}}"
        except (TypeError, ValueError):
            return f"{obj:{specifier}}"
    s = pformat_collection(obj, **with_indent)
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
            raise TypeError(f"register expected a type for cls, got {cls!r}")
    def decorator(func: Formatter[T]) -> Formatter[T]:
        if not callable(func):
            raise TypeError(f"@register expected a formatter function, got {func!r}")
        FORMATTERS.extend((cls, func) for cls in args)
        return func
    return decorator

def align(indentations: Mapping[int, int]) -> Mapping[int, bool]:
    """
    Estimates reasonable alignments for key-value pairs by grouping
    nearby alignments to the deeper indentation.
    """
    L = sorted(indentations)
    moved = 0
    unmoved = 0
    is_moved = [False] * len(L)
    for i in reversed(range(len(L))):
        if i + 1 < len(L):
            temp = unmoved + indentations[L[i + 1]] - indentations[L[i]] + 1
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

@register(UserDict, dict)
def pformat_dict(obj: Mapping[Any, Any], specifier: str, depth: int, indent: int, shorten: bool, json: bool) -> str:
    """Formats a mapping as a dict."""
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten, json=json)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten, json=json)
    plus_plus_indent = dict(specifier=specifier, depth=depth_plus + indent, indent=indent, shorten=shorten, json=json)
    if len(obj) < 10:
        keys = [pformat(key, **no_indent) for key in obj]
        values = [pformat(value, **no_indent) for value in obj.values()]
        s = ", ".join([f"{k}: {v}" for k, v in zip(keys, values)])
        if len(s) < 50 and "\n" not in s:
            return f"{{{s}}}"
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
    if len(s) < 100 and "\n" not in s:
        return f"{{{s}}}"
    indentations = Counter(
        (len(c[0]) + indent - 1) // indent
        for c in content
        if c is not ...
        if len(c[0]) + len(c[1]) < 90
        if "\n" not in c[0]
        if "\n" not in c[1]
    )
    alignment = align(indentations)
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
                    + f": {c[1]}"
                )
                    if
                (
                    len(c[0]) + len(c[1]) < 90
                    and "\n" not in c[0]
                    and "\n" not in c[1]
                )
                    else
                (
                    f"{c[0]}:\n"
                    + " " * (depth_plus + indent)
                    + c[1]
                )
                for c in content
            ])
        + (",\n" + " " * depth + "}")
    )

def pformat_collection(obj: Collection[Any], specifier: str, depth: int, indent: int, shorten: bool, json: bool) -> str:
    """Formats as an collection as a list without the enclosing brackets."""
    depth_plus = depth + indent
    no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten, json=json)
    plus_indent = dict(specifier=specifier, depth=depth_plus, indent=indent, shorten=shorten, json=json)
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
