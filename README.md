# prettyformatter

Pretty formatter enables pretty formatting using hanging indents,
dataclasses, ellipses, and simple customizability by registering
formatters.

## Installation

Windows:

```
py -m pip install prettyformatter
```

Unix/MacOS:

```
python3 -m pip install prettyformatter
```

## Imports

```python
from prettyformatter import PrettyClass, PrettyDataclass, pprint, pformat, register
```

## Basic Usage

Long containers are truncated.

```python
pprint(list(range(1000)))
"""
[0, 1, 2, 3, 4, ..., 997, 998, 999]
"""
```

Large nested structures are split into multiple lines, while things
which (reasonably) fit on a line will remain on one line.

Notice that trailing commas are used.

Notice that multi-line dictionaries have key-value pairs indented
at different levels.

```python
pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}])
"""
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
"""
```

The current depth and indentation size can be modified.
Shortening the data is also toggleable.
See `help(prettyformatter.pprint)` for more information.

```python
pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}], indent=2)
"""
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
"""
```

The pretty string can be used elsewhere.

```python
s = pformat([{i: {"ABC": [list(range(30))]} for i in range(5)}])

print(s)
"""
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
"""
```

Dataclasses are supported by subclassing the PrettyDataclass.

```python
from dataclasses import dataclass
from typing import List

big_data = list(range(1000))
```

Dataclass fields are pretty formatted.

```python
@dataclass
class Data(PrettyDataclass):
    data: List[int]


print(Data(big_data))
"""
Data(data=[0, 1, 2, 3, 4, ..., 997, 998, 999])
"""
```

Long dataclasses are split into multiple lines.

```python
@dataclass
class MultiData(PrettyDataclass):
    x: List[int]
    y: List[int]
    z: List[int]


print(MultiData(big_data, big_data, big_data))
"""
MultiData(
    x=[0, 1, 2, 3, 4, ..., 997, 998, 999],
    y=[0, 1, 2, 3, 4, ..., 997, 998, 999],
    z=[0, 1, 2, 3, 4, ..., 997, 998, 999],
)
"""
```

Nested data is indented deeper.

```python
@dataclass
class NestedData(PrettyDataclass):
    data: List[List[int]]


print(NestedData([big_data] * 1000))
"""
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
"""
```

If there are more than 3 fields, then fields and their values are
split, similar to a dict.

```python
@dataclass
class Person(PrettyDataclass):
    name: str
    birthday: str
    phone_number: str
    address: str


print(Person("Jane Doe", "2001-01-01", "012-345-6789", "123 Sample St."))
"""
Person(
    name=
        'Jane Doe',
    birthday=
        '2001-01-01',
    phone_number=
        '012-345-6789',
    address=
        '123 Sample St.',
)
"""
```

Named tuples work like dataclasses, but requires `pprint` instead of
`print`.

```python
from typing import NamedTuple

big_data = list(range(1000))


class Data(NamedTuple):
    data: List[int]


pprint(Data(big_data))
"""
Data(data=[0, 1, 2, 3, 4, ..., 997, 998, 999])
"""
```

Custom formatters for your classes can be defined.

```python
class PrettyHelloWorld(PrettyClass):

    def __pformat__(self, specifier, depth, indent, shorten):
        return f"Hello world! Got {specifier!r}, {depth}, {indent}, {shorten}."


print(PrettyHelloWorld())
"""
Hello world! Got '', 0, 4, True.
"""
```

Use f-strings with your classes.

```
"""
format_spec ::= [[[shorten|]depth>>]indent:][specifier]
shorten     ::= T | F
depth       ::= digit+
indent      ::= digit+ without leading 0
specifier   ::= anything else you want to support e.g. ".2f"
"""

print(f"{PrettyHelloWorld():F|5>>6:.2f}")
"""
Hello World! Got '.2f', 5, 6, False.
"""
```

Custom formatters for existing classes can be registered.

```python
import numpy as np

@register(np.ndarray)
def pformat_ndarray(obj, specifier, depth, indent, shorten):
    with np.printoptions(formatter=dict(all=lambda x: format(x, specifier))):
        return repr(obj).replace("\n", "\n" + " " * depth)

pprint(dict.fromkeys("ABC", np.arange(9).reshape(3, 3)))
"""
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
```
