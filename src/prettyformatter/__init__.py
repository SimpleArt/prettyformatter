"""
Pretty formatter enables pretty formatting using hanging indents,
dataclasses, ellipses, and simple customizability by registering
formatters.

Examples
---------
    Imports:
        >>> from prettyformatter import PrettyDataclass, pprint, pformat, register

    Long containers are truncated:
        >>> pprint(list(range(1000)))
        [0, 1, 2, 3, 4, ..., 997, 998, 999]

    Large nested structures are split into multiple lines, while things
    which (reasonably) fit on a line will remain on one line.
    
    Notice that trailing commas are used.

    Notice that multi-line dictionaries have key-value pairs indented
    at different levels.
        >>> pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}])
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

    The current depth and indentation size can be modified.
        >>> pprint([{i: {"ABC": [list(range(30))]} for i in range(5)}], indent=2)
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

    Dataclasses are supported by subclassing the PrettyDataclass.
        >>> from dataclasses import dataclass
        >>> from typing import List
        >>> 
        >>> bit_data = list(range(1000))
        >>> 
        >>> @dataclass
        ... class Data(PrettyDataclass):
        ...     data: List[int]
        ... 
        >>> Data(big_data)
        Data(data=[0, 1, 2, 3, 4, ..., 997, 998, 999])
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

    Register custom formatters.
        >>> import numpy as np
        >>> 
        >>> @register(np.ndarray)
        ... def pformat_ndarray(obj, specifier, depth, indent):
        ...     with np.printoptions(formatter=dict(all=lambda x: format(x, specifier))):
        ...         return repr(obj).replace(\"\\n\", \"\\n\" + \" \" * depth)
        ... 
        >>> pprint(dict.fromkeys("ABC", np.arange(9).reshape(3, 3)))
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
__version__ = "1.1.2"

from ._prettyformatter import PrettyDataclass, pformat, pprint, register
