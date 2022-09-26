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

|  | `prettyformatter` | `json.dumps` | `pprint.pprint` | `IPython` | `yaml.dump` |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Repr | Y | Y<sup>[1]</sup> | Y | Y | N |
| JSON | Y | Y | N<sup>[2]</sup> | N<sup>[2]</sup> | N |
| H-Compact | Y | Y | N | Y | Y |
| V-Compact | Y | N | Y | Y | N |
| Short Output | Y | N | N | Y | N |
| Align Dict Values | Y | N | N | N | N |
| Align List | Y | Y | Y | N | Y |
| Dataclasses | Y | N | Y | Y | Y<sup>[3]</sup> |
| Named Tuples | Y | Y<sup>[3]</sup> | Y | Y | Y<sup>[3]</sup> |
| Numpy Arrays | Y | N | N | Y | N |

[1]: Turns `None` into `"null"`.

[2]: Works for JSON which only uses dictionaries, lists, and numeric
values. Does not work with `None` (`"null"`), `math.inf` (`"Infinity"`),
`math.nan` (`"NaN"`), strings (`'"strings"'` not `"'strings'"`), or
booleans (`"true"` and `"false"`).

[3]: Although supported, does not produce valid reprs e.g. `(1, 2) -> [1, 2]`.

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
