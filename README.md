# prettyformatter

Pretty formatter enables pretty formatting using aligned and hanging
indents for JSON, dataclasses, named tuples, and any custom formatted
object such as Numpy arrays.

For the full documentation, see
[here](https://simpleart.github.io/prettyformatter/).

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

`prettyformatter` works with JSON data.

```python
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
```

## `pprint`:

`prettyformatter` attempts to compromise between alignment,
readability, and horizontal/vertical compactness.

Support for JSON data is also as easy as `pprint(json=True)`.

```python
from prettyformatter import pprint

pprint(data, json=True)
"""
{
    "id"    : "0001",
    "type"  : "donut",
    "name"  : "Cake",
    "ppu"   : 0.55,
    "batters":
        [
            {"id": "1001", "type": "Regular"},
            {"id": "1002", "type": "Chocolate"},
            {"id": "1003", "type": "Blueberry"},
            {"id": "1004", "type": "Devil's Food"}
        ],
    "topping":
        [
            {"id": "5001", "type": None},
            {"id": "5002", "type": "Glazed"},
            {"id": "5005", "type": "Sugar"},
            {"id": "5007", "type": "Powdered Sugar"},
            {"id": "5006", "type": "Chocolate with Sprinkles"},
            {"id": "5003", "type": "Chocolate"},
            {"id": "5004", "type": "Maple"}
        ]
}
"""
```

`pprint` supports the same parameters as `print`, meaning saving to
files is as easy as `file=file`.

```python
from prettyformatter import pprint

with open("cake.json", mode="w") as file:
    pprint(data, json=True, file=file)
```

## `PrettyDataclass`

`prettyformatter` supports dataclasses easily.

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

## `register`

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
    "A" : [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
    "B" : [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
    "C" : [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
}
"""
```
