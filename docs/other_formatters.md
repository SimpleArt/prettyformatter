# Formatter Comparisons

Compared to other formatters, Pretty Formatter attempts to find a
balance between vertical and horizontal compactness as well as
readability. For example, Python's `pprint.pprint` suffers greatly from
lack of horizontal compactness, while `json.dumps` suffers from
vertical compactness for small things. Additionally, neither of them
attempt to align dictionary values, which can make it hard to read the
actual data stored within. For larger amounts of data, IPython's
approach of truncating the output can also make it easier to understand
data which has clearly repeating patterns. Pretty Formatter takes a
middle ground on many of these cases, expanding the data into multiple
lines only when reasonably necessary and offering the option to
truncate the outputs, enabled by default, similar to IPython.

Aside from formatting structure, not all formatters support JSON,
dataclasses, named tuples, or Numpy arrays, and some may only support
some partially. The table below compares these features for the
previously mentioned formatters.

| Formatter | Repr | JSON | H-Compact | V-Compact | Short Output | Align Dict Value | Align List | Dataclasses | Named Tuples | Numpy Arrays |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | 
| `prettyformatter` | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `json.dumps` | Y<sup>[1]</sup> | Y | Y | N | N | N | Y | N | Y<sup>[2]</sup> | N |
| `pprint.pprint` | Y | N<sup>[3]</sup> | N | Y | N | N | Y | Y | Y | N |
| `IPython` | Y | N<sup>[3]</sup> | Y | Y | Y | N | N | Y | Y | Y |
| `yaml.dump` | N | N | Y | N | N | N | Y | Y<sup>[2]</sup> | Y<sup>[2]</sup> | N |

[1]: Turns `None` into `"null"`.

[2]: Although supported, does not produce valid reprs e.g. `(1, 2) -> [1, 2]`.

[3]: Works for JSON which only uses dictionaries, lists, and numeric values.
Does not work with `None` (`"null"`), strings (`'"strings"'` not `"'strings'"`), or booleans (`"true"` and `"false"`).

## Installation

### Windows:

```
py -m pip install prettyformatter IPython yaml
```

### Unix/MacOS:

```
python3 -m pip install prettyformatter IPython yaml
```

## JSON Example

### Data:

```python
batters = [
    {"id": "1001", "type": "Regular"},
    {"id": "1002", "type": "Chocolate"},
    {"id": "1003", "type": "Blueberry"},
    {"id": "1004", "type": "Devil's Food"},
]

toppings = [
    {"id": "5001", "type": "None"},
    {"id": "5002", "type": "Glazed"},
    {"id": "5005", "type": "Sugar"},
    {"id": "5007", "type": "Powdered Sugar"},
    {"id": "5006", "type": "Chocolate with Sprinkles"},
    {"id": "5003", "type": "Chocolate"},
    {"id": "5004", "type": "Maple"},
]

data = {"id": "0001", "type": "donut", "name": "Cake", "ppu": 0.55, "batters": batters, "topping": toppings}
```

### Pretty Formatter

```python

from prettyformatter import pprint

pprint(data)
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
            {"id": "1004", "type": "Devil's Food"},
        ],
    "topping":
        [
            {"id": "5001", "type": None},
            {"id": "5002", "type": "Glazed"},
            {"id": "5005", "type": "Sugar"},
            {"id": "5007", "type": "Powdered Sugar"},
            {"id": "5006", "type": "Chocolate with Sprinkles"},
            {"id": "5003", "type": "Chocolate"},
            {"id": "5004", "type": "Maple"},
        ],
}
"""
```

### `pprint.pprint`

```python
from pprint import pprint

pprint(data)
"""
{'batters': [{'id': '1001', 'type': 'Regular'},
             {'id': '1002', 'type': 'Chocolate'},
             {'id': '1003', 'type': 'Blueberry'},
             {'id': '1004', 'type': "Devil's Food"}],
 'id': '0001',
 'name': 'Cake',
 'ppu': 0.55,
 'topping': [{'id': '5001', 'type': 'None'},
             {'id': '5002', 'type': 'Glazed'},
             {'id': '5005', 'type': 'Sugar'},
             {'id': '5007', 'type': 'Powdered Sugar'},
             {'id': '5006', 'type': 'Chocolate with Sprinkles'},
             {'id': '5003', 'type': 'Chocolate'},
             {'id': '5004', 'type': 'Maple'}],
 'type': 'donut'}
"""
```

### `json.dumps`

```python
import json

print(json.dumps(data, indent=4))
"""
{
    "id": "0001",
    "type": "donut",
    "name": "Cake",
    "ppu": 0.55,
    "batters": [
        {
            "id": "1001",
            "type": "Regular"
        },
        {
            "id": "1002",
            "type": "Chocolate"
        },
        {
            "id": "1003",
            "type": "Blueberry"
        },
        {
            "id": "1004",
            "type": "Devil's Food"
        }
    ],
    "topping": [
        {
            "id": "5001",
            "type": "None"
        },
        {
            "id": "5002",
            "type": "Glazed"
        },
        {
            "id": "5005",
            "type": "Sugar"
        },
        {
            "id": "5007",
            "type": "Powdered Sugar"
        },
        {
            "id": "5006",
            "type": "Chocolate with Sprinkles"
        },
        {
            "id": "5003",
            "type": "Chocolate"
        },
        {
            "id": "5004",
            "type": "Maple"
        }
    ]
}
"""
```

### `IPython`

```python
from IPython.lib.pretty import pretty

print(pretty(data))
"""
{'id': '0001',
 'type': 'donut',
 'name': 'Cake',
 'ppu': 0.55,
 'batters': [{'id': '1001', 'type': 'Regular'},
  {'id': '1002', 'type': 'Chocolate'},
  {'id': '1003', 'type': 'Blueberry'},
  {'id': '1004', 'type': "Devil's Food"}],
 'topping': [{'id': '5001', 'type': 'None'},
  {'id': '5002', 'type': 'Glazed'},
  {'id': '5005', 'type': 'Sugar'},
  {'id': '5007', 'type': 'Powdered Sugar'},
  {'id': '5006', 'type': 'Chocolate with Sprinkles'},
  {'id': '5003', 'type': 'Chocolate'},
  {'id': '5004', 'type': 'Maple'}]}
"""
```

### `yaml.dump`

```python
import yaml

print(yaml.dump(data, default_flow_style=False))
"""
batters:
- id: '1001'
  type: Regular
- id: '1002'
  type: Chocolate
- id: '1003'
  type: Blueberry
- id: '1004'
  type: Devil's Food
id: '0001'
name: Cake
ppu: 0.55
topping:
- id: '5001'
  type: None
- id: '5002'
  type: Glazed
- id: '5005'
  type: Sugar
- id: '5007'
  type: Powdered Sugar
- id: '5006'
  type: Chocolate with Sprinkles
- id: '5003'
  type: Chocolate
- id: '5004'
  type: Maple
type: donut
"""
```
