# Rest Extension

Extension for Restful web services.
It requires [apispec][] and [marshmallow][] packages:
```python
EXTENSIONS = [
    ...,
    'lux.extensions.rest',
    ...
]
```

## Token Backend

This extensions implements an abstract authentication backend based on **authorization tokens**,
the ``lux.extensions.rest.TokenBackend``.



[apispec]: https://github.com/marshmallow-code/apispec
[marshmallow]: https://github.com/marshmallow-code/marshmallow
