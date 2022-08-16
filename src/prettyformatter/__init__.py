"""
Pretty formatter enables pretty formatting using hanging indents for
JSON, dataclasses, named tuples, and any custom formatted object such
as Numpy arrays.

For the full documentation, see:
    https://simpleart.github.io/prettyformatter/

Examples
---------
    Imports:
        >>> from prettyformatter import PrettyClass, PrettyDataclass
        >>> from prettyformatter import pprint, pformat, register

    JSON Data:
        >>> batters = [
        ...     {"id": "1001", "type": "Regular"},
        ...     {"id": "1002", "type": "Chocolate"},
        ...     {"id": "1003", "type": "BlueBerry"},
        ...     {"id": "1004", "type": "Devil's Food"},
        ... ]
        >>> 
        >>> toppings = [
        ...     {"id": "5001", "type": None},
        ...     {"id": "5002", "type": "Glazed"},
        ...     {"id": "5005", "type": "Sugar"},
        ...     {"id": "5007", "type": "Powdered Sugar"},
        ...     {"id": "5006", "type": "Chocolate with Sprinkles"},
        ...     {"id": "5003", "type": "Chocolate"},
        ...     {"id": "5004", "type": "Maple"},
        ... ]
        >>> 
        >>> data = {"id": "0001", "type": "donut", "name": "Cake", "ppu": 0.55, "batters": batters, "topping": toppings}

    JSON Data Printing:
        >>> pprint(data, json=True)
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
                    {"id": "1003", "type": "BlueBerry"},
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

    JSON Data File:
        >>> with open("cake.json", mode="w") as file:
        ...     pprint(data, json=True, file=file)
        ... 

    IPython-styled Shorted Output:
        >>> pprint(list(range(1000)))
        [0, 1, 2, 3, 4, ..., 997, 998, 999]

    Indentation:
        >>> pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}])
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

    Custom Indentation:
        >>> pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}], indent=2)
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

    Files:
        >>> with open("example.txt", mode="w") as file:
        ...     pprint(data, file=file)
        ... 
        >>> with open("example.json", mode="w") as file:
        ...     pprint(data, json=True, file=file)
        ... 

    Pretty Formatted String:
        >>> s = pformat([{i: {"ABC": [list(range(30))]} for i in range(5)}])
        >>> print(s)
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

    Dataclasses:
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
            name=
                'Jane Doe',
            birthday=
                '2001-01-01',
            phone_number=
                '012-345-6789',
            address=
                '123 Sample St.',
        )

    Custom Formatters:
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
            "A":
                [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
            "B":
                [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
            "C":
                [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
        }
"""
__version__ = "1.4.4"

from ._pretty_class import PrettyClass
from ._pretty_dataclass import PrettyDataclass
from ._prettyformatter import pformat, pprint, register
