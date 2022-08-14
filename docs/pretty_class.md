# PrettyClass

Base class for implementing pretty classes.

Defines `__format__`, `__str__`, and `__repr__` using `pformat`.

Implement `__pformat__` for custom `pformat` behavior.

## Example

```python
from prettyformatter import PrettyClass, pprint


class PrettyHelloWorld(PrettyClass):
    
    def __pformat__(self, specifier, depth, indent, shorten, json):
        return f"Hello world! Got {specifier!r}, {depth}, {indent}, {shorten}, {json}."


print(PrettyHelloWorld())
"""
Hello world! Got '', 0, 4, True, False.
"""

print(f"{PrettyHelloWorld():F|5>>6:.2f}")
"""
Hello world! Got '.2f', 5, 6, False, False.
"""

pprint(PrettyHelloWorld(), json=True)
"""
Hello world! Got '', 0, 4, False, True.
"""
```
