# Rest Extension

Extension for Restful web services.

When using default lux extensions, the usual position of this extension is
just after the `lux.extensions.base`:
```python
EXTENSIONS = [
    'lux.extensions.base',
    'lux.extensions.rest',
    ...
]
```
            
## Token Backend

This extensions implements an abstract authentication backend based on **authorization tokens**,
the ``lux.extensions.rest.TokenBackend``.
