# Applications

The ``applications`` extension allows to use lux with multiple applications.

## Master Application

The master application is the main application in this extensions, it must be always present.
Its ``ID`` is given by the configuration parameter ``MASTER_APPLICATION_ID``.
Before using this extension you need to create an ID, you can do so by
running:
```
python manage.py create_uuid
```
and copy and paste the UUID into the config file.

## Multi backend

Backend which allow to run multiple lux applications in a single application domain.
To use the backend, add it as **first** to the list of authentication
backends:
```
AUTH_BACKENDS = [
    "lux.extensions.applications.MultiBackend",
    ...
]
```
