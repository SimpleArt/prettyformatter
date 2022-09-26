# PrettyDataclass

Base class for creating pretty dataclasses.

## Import

```python
from prettyformatter import PrettyDataclass
```

## Examples

### Pretty Attributes

All attributes are pretty formatted.

```python
from dataclasses import dataclass
from typing import List


@dataclass
class Data(PrettyDataclass):
    data: List[int]


print(Data(list(range(1000))))
"""
Data(data=[0, 1, 2, 3, 4, ..., 997, 998, 999])
"""
```

### Multi-line Formatting

If it gets too long, the dataclass is split into multiple lines.

```python
from dataclasses import dataclass
from typing import List


@dataclass
class MultiData(PrettyDataclass):
    x: List[int]
    y: List[int]
    z: List[int]


data = list(range(1000))
print(MultiData(data, data, data))
"""
MultiData(
    x=[0, 1, 2, 3, 4, ..., 997, 998, 999],
    y=[0, 1, 2, 3, 4, ..., 997, 998, 999],
    z=[0, 1, 2, 3, 4, ..., 997, 998, 999],
)
"""
```

### Nested Indentation

Attributes that require multiple lines are indented an extra time for
visual contrast with the attribute names.

```python
from dataclasses import dataclass
from typing import List


@dataclass
class NestedData(PrettyDataclass):
    data: List[List[int]]


print(NestedData([list(range(1000))] * 1000))
"""
NestedData(
    data=
        [
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
"""
```

### Many Fields

If there are more than 3 fields or the field names are not short and
alignable, then the names and values are aligned similar to a
dictionary.

```python
from dataclasses import dataclass


@dataclass
class Person(PrettyDataclass):
    name: str
    birthday: str
    phone_number: str
    address: str


print(Person("Jane Doe", "2001-01-01", "012-345-6789", "123 Sample St."))
"""
Person(
    name        = "Jane Doe",
    birthday    = "2001-01-01",
    phone_number    = "012-345-6789",
    address     = "123 Sample St.",
)
"""
```
