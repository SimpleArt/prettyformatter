"""
Implements:
    PrettyDataclass
"""
import sys
from dataclasses import fields, is_dataclass
from typing import Any, TypeVar

if sys.version_info < (3, 9):
    from typing import Dict, Type
else:
    from builtins import dict as Dict, type as Type

from ._pretty_class import PrettyClass
from ._prettyformatter import pformat

Self = TypeVar("Self", bound="PrettyDataclass")


class PrettyDataclass(PrettyClass):
    """
    Base class for creating pretty dataclasses.

    For the full documentation, see:
        https://simpleart.github.io/prettyformatter/PrettyDataclass

        >>> from dataclasses import dataclass
        >>> from typing import List
        >>> 
        >>> 
        >>> @dataclass
        ... class Data(PrettyDataclass):
        ...     data: List[int]
        ... 
        >>> 
        >>> Data(list(range(1000)))
        Data(data=[0, 1, 2, 3, 4, ..., 997, 998, 999])
        >>> 
        >>> 
        >>> @dataclass
        ... class Person(PrettyDataclass):
        ...     name: str
        ...     birthday: str
        ...     phone_number: str
        ...     address: str
        ... 
        >>> 
        >>> Person("Jane Doe", "2001-01-01", "012-345-6789", "123 Sample St.")
        Person(
            name        = "Jane Doe",
            birthday    = "2001-01-01",
            phone_number    = "012-345-6789",
            address     = "123 Sample St.",
        )
    """

    __slots__ = ()

    def __init_subclass__(cls: Type[Self], **kwargs: Any) -> None:
        """Overrides the `__repr__` with itself."""
        # Save the __repr__ directly onto the subclass so that
        # @dataclass will actually notice it.
        cls.__repr__ = cls.__repr__
        return super().__init_subclass__(**kwargs)

    def __pkwargs__(self: Self) -> Dict[str, Any]:
        """
        Implements pretty formatting for dataclasses based on the
        dataclass fields. If the subclass is not a dataclass, does not
        use the dataclass implementation.
        """
        cls = type(self)
        if not is_dataclass(cls):
            raise NotImplementedError
        return {f.name: getattr(self, f.name) for f in fields(cls)}
