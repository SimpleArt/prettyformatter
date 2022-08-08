"""
Implements:
    PrettyDataclass
"""
from dataclasses import fields, is_dataclass
from typing import Any, Type, TypeVar

from ._pretty_class import PrettyClass
from ._prettyformatter import pformat

Self = TypeVar("Self", bound="PrettyDataclass")


class PrettyDataclass(PrettyClass):
    """
    Base class for creating pretty dataclasses.

    Dataclasses are supported by subclassing the PrettyDataclass.
        >>> from dataclasses import dataclass
        >>> from typing import List
        >>> 
        >>> big_data = list(range(1000))

    Dataclass fields are pretty formatted.
        >>> @dataclass
        ... class Data(PrettyDataclass):
        ...     data: List[int]
        ... 
        >>> Data(big_data)
        Data(data=[0, 1, 2, 3, 4, ..., 997, 998, 999])

    Long dataclasses are split into multiple lines.
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

    Nested data is indented deeper.
        >>> @dataclass
        ... class NestedData(PrettyDataclass):
        ...     data: List[List[int]]
        ... 
        >>> NestedData([big_data] * 1000)
        NestedData(
            data=[
                    [0, 1, 2, 3, 4, ..., 997, 998, 999],
                    [0, 1, 2, 3, 4, ..., 997, 998, 999],
                    [0, 1, 2, 3, 4, ..., 997, 998, 999],
                    [0, 1, 2, 3, 4, ..., 997, 998, 999],
                    [0, 1, 2, 3, 4, ..., 997, 998, 999],
                    ...,
                    [0, 1, 2, 3, 4, ..., 997, 998, 999],
                    [0, 1, 2, 3, 4, ..., 997, 998, 999],
                    [0, 1, 2, 3, 4, ..., 997, 998, 999],
                ],
        )

    If there are more than 3 fields and the dataclass is long,
    then fields and their values are split, similar to a dict.
        >>> @dataclass
        ... class Person(PrettyDataclass):
        ...     name: str
        ...     birthday: str
        ...     phone_number: str
        ...     address: str
        ... 
        >>> Person("Jane", "2001-01-01", "012-345-6789", "123 Sample St.")
        Person(
            name=
                'Jane',
            birthday=
                '2001-01-01',
            phone_number=
                '012-345-6789',
            address=
                '123 Sample St.',
        )
    """

    __slots__ = ()

    def __init_subclass__(cls: Type[Self], **kwargs: Any) -> None:
        """Overrides the `__repr__` with itself."""
        # Save the __repr__ directly onto the subclass so that
        # @dataclass will actually notice it.
        cls.__repr__ = cls.__repr__
        return super().__init_subclass__(**kwargs)

    def __pformat__(self: Self, specifier: str, depth: int, indent: int, shorten: bool) -> str:
        """
        Implements pretty formatting for dataclasses based on the
        dataclass fields. If the subclass is not a dataclass, returns
        the parent implementation of format(self, specifier).
        """
        cls = type(self)
        if not is_dataclass(cls):
            return super(PrettyClass, cls).__format__(self, specifier)
        depth_plus = depth + indent
        no_indent = dict(specifier=specifier, depth=0, indent=indent, shorten=shorten)
        plus_plus_indent = dict(specifier=specifier, depth=depth_plus + indent, indent=indent, shorten=shorten)
        if len(fields(cls)) > 3:
            return (
                (f"{cls.__name__}(\n" + " " * depth_plus)
                + (",\n" + " " * depth_plus).join([
                        f"{f.name}=\n    "
                        + " " * depth_plus
                        + pformat(getattr(self, f.name), **plus_plus_indent)
                        for f in fields(cls)
                    ])
                + (",\n" + " " * depth + ")")
            )
        s = (
            f"{cls.__name__}("
            + ", ".join([
                    f"{f.name}={pformat(getattr(self, f.name), **no_indent)}"
                    for f in fields(cls)
                ])
            + ")"
        )
        if len(s) < 25 and "\n" not in s or len(s) < 50:
            if "\n" not in s:
                return s
            return (
                (f"{cls.__name__}(\n" + " " * depth_plus)
                + (",\n" + " " * depth_plus).join([
                        f"{f.name}="
                        + pformat(getattr(self, f.name), **no_indent).replace("\n", "\n    " + " " * depth_plus)
                        for f in fields(cls)
                    ])
                + (",\n" + " " * depth + ")")
            )
        if len({len(f.name) for f in fields(cls)}) > 1:
            return (
                (f"{cls.__name__}(\n" + " " * depth_plus)
                + (",\n" + " " * depth_plus).join([
                        f"{f.name}=\n    "
                        + " " * depth_plus
                        + pformat(getattr(self, f.name), **plus_plus_indent)
                        for f in fields(cls)
                    ])
                + (",\n" + " " * depth + ")")
            )
        return (
            (f"{cls.__name__}(\n" + " " * depth_plus)
            + (",\n" + " " * depth_plus).join([
                    f"{f.name}="
                    + pformat(getattr(self, f.name), **plus_plus_indent)
                    for f in fields(cls)
                ])
            + (",\n" + " " * depth + ")")
        )
