# PrettyFormatter

Pretty Formatter enables pretty formatting using hanging indents for
JSON, dataclasses, named tuples, and any custom formatted object such
as Numpy arrays.

For a comparison to other pretty formatters, see
[Comparison](https://simpleart.github.io/prettyformatter/comparison/).

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
from prettyformatter import PrettyClass, PrettyDataclass
from prettyformatter import pprint, pformat, register
```

## JSON Data

```python
from prettyformatter import pprint

batters = [
    {"id": "1001", "type": "Regular"},
    {"id": "1002", "type": "Chocolate"},
    {"id": "1003", "type": "Blueberry"},
    {"id": "1004", "type": "Devil's Food"},
]

toppings = [
    {"id": "5001", "type": None},
    {"id": "5002", "type": "Glazed"},
    {"id": "5005", "type": "Sugar"},
    {"id": "5007", "type": "Powdered Sugar"},
    {"id": "5006", "type": "Chocolate with Sprinkles"},
    {"id": "5003", "type": "Chocolate"},
    {"id": "5004", "type": "Maple"},
]

data = {"id": "0001", "type": "donut", "name": "Cake", "ppu": 0.55, "batters": batters, "topping": toppings}

pprint(data, json=True)
"""
{
    "id":
        "0001",
    "type":
        "donut",
    "name":
        "Cake",
    "ppu":
        0.55,
    "batters":
        [
            {"id": "1001", "type": "Regular"},
            {"id": "1002", "type": "Chocolate"},
            {"id": "1003", "type": "Blueberry"},
            {"id": "1004", "type": "Devil's Food"},
        ],
    "topping":
        [
            {"id": "5001", "type": null},
            {"id": "5002", "type": "Glazed"},
            {"id": "5005", "type": "Sugar"},
            {"id": "5007", "type": "Powdered Sugar"},
            {"id": "5006", "type": "Chocolate with Sprinkles"},
            {"id": "5003", "type": "Chocolate"},
            {"id": "5004", "type": "Maple"},
        ],
}
"""

# Save to a file.
with open("cake.json", mode="w") as file:
    pprint(data, json=True, file=file)
```

## IPython-styled Shortened Output

```python
pprint(list(range(30)))
"""
[0, 1, 2, 3, 4, ..., 27, 28, 29]
"""

pprint(list(range(30)), shorten=False)
"""
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
"""
```

## Indentation

Pretty Formatter uses hanging indents when necessary. For dictionaries,
keys are considered 1 indent deep and values are considered 2 indents
deep.

### Small Output

```python
{outer: inner}
```

### Large Output

```python
{
    outer:
        inner,
}
```

By not splitting the output into multiple lines when everything fits
reasonably in one line, the output can be made considerably more
compact than `json.dumps`.

```python
from prettyformatter import pprint

pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}])
"""
[
    {
        0:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        1:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        2:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        3:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        4:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
    },
]
"""
```

The current depth and indentation size can also be modified.

```python
from prettyformatter import pprint

pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}], indent=2)
"""
[
  {
    0:
      {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
    1:
      {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
    2:
      {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
    3:
      {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
    4:
      {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
  },
]
"""

pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}], depth=4, indent=2)
"""
[
      {
        0:
          {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        1:
          {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        2:
          {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        3:
          {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        4:
          {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
      },
    ]
"""
```

## Beyond Printing

### Files

Files can be written to, similar to using `print(file=file)`.

```python
with open("example.txt", mode="w") as file:
    pprint(data, file=file)
```

```python
with open("example.json", mode="w") as file:
    pprint(data, json=True, file=file)
```

### Pretty Formatted Strings

While `pprint` prints the result, `pformat` returns it.

```python
s = pformat([{i: {"ABC": [list(range(30))]} for i in range(5)}])

print(s)
"""
[
    {
        0:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        1:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        2:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        3:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
        4:
            {"ABC": [[0, 1, 2, 3, 4, ..., 27, 28, 29]]},
    },
]
"""
```

## Custom Classes

### Dataclasses:

Dataclasses are supported by subclassing the `PrettyDataclass`. Pretty
formatting a dataclass causes its fields to be pretty printed.

```python
from dataclasses import dataclass
from typing import List

from prettyformatter import PrettyDataclass


@dataclass
class Data(PrettyDataclass):
    data: List[int]


print(Data(list(range(1000))))
"""
Data(data=[0, 1, 2, 3, 4, ..., 997, 998, 999])
"""
```

If the dataclass does not fit on one line, then its fields are split
into multiple lines. 

```python
from dataclasses import dataclass
from typing import List

from prettyformatter import PrettyDataclass


@dataclass
class MultiData(PrettyDataclass):
    x: List[int]
    y: List[int]
    z: List[int]


L = list(range(1000))
print(MultiData(L, L, L))
"""
MultiData(
    x=[0, 1, 2, 3, 4, ..., 997, 998, 999],
    y=[0, 1, 2, 3, 4, ..., 997, 998, 999],
    z=[0, 1, 2, 3, 4, ..., 997, 998, 999],
)
"""
```

Field values are indented deeper than field names.

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

If there are 3 or fewer fields, their field names are aligned, and each
field fits on one line,

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
        "Jane Doe",
    birthday=
        "2001-01-01",
    phone_number=
        "012-345-6789",
    address=
        "123 Sample St.",
)
"""
```

### Tuples:
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

### Custom formatters:
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

```python
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
def pformat_ndarray(obj, specifier, depth, indent, shorten, json):
    if json:
        return pformat(obj.tolist(), specifier, depth, indent, shorten, json)
    with np.printoptions(formatter=dict(all=lambda x: format(x, specifier))):
        return repr(obj).replace("\n", "\n" + " " * depth)

pprint(dict.fromkeys("ABC", np.arange(9).reshape(3, 3)))
"""
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
"""

pprint(dict.fromkeys("ABC", np.arange(9).reshape(3, 3)), json=True)
"""
{
    "A":
        [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
    "B":
        [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
    "C":
        [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
}
"""
```