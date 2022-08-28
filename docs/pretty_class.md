# PrettyClass

Base class for implementing pretty classes.

Defines `__format__`, `__str__`, and `__repr__` using `pformat`.

Dunders
---------

Implement `__pargs__` and/or `__pkwargs__` if the desired `pformat` is
`cls_name(*args, **kwargs)`.

```python
from prettyformatter import PrettyClass


class Dog(PrettyClass):

    def __init__(self, name, **kwargs):
        self.name = name
        self.attributes = kwargs

    def __pargs__(self):
        return (self.name,)

    def __pkwargs__(self):
        return self.attributes


print(Dog("Fido", age=3))
"""
Dog("Fido", age=3)
"""
```

Implement `__pformat__` for more customized `pformat` behavior.

```python
from prettyformatter import PrettyClass, pprint


class PrettyHelloWorld(PrettyClass):
    
    def __pformat__(self, specifier, depth, indent, shorten, json):
        return f"Hello world! Got {specifier!r}, {depth}, {indent}, {shorten}, {json}."


print(PrettyHelloWorld())
"""
Hello world! Got '', 0, 4, True, False.
"""

JSON serialization
--------------------

If the default `__pformat__` is used and `__pargs__` and/or
`__pkwargs__` is implemented, then JSON serialization is done by
converting the `args` into a `list` and the `kwargs` into a `dict`. If
both are given, they are combined using the format of
`{"class": cls_name, "args": list(args), "kwargs": kwargs}`.

```python
pprint(Dog("Fido", age=3), json=True)
"""
{"class": "Dog", "args": ["Fido"], "kwargs": {"age": 3}}
"""
```
