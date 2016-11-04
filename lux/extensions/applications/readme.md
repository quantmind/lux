# Applications

The ``applications`` extension allows to use lux with multiple applications.

## Admin Application

The admin application is the main application in this extensions, it must be always present.
Its id is given by the configuration parameter ``MASTER_APPLICATION_ID``.
Before using this extension you need to create an ID, you can do so by
running:
```
python manage.py create_uuid
```
and copy and paste the UUID into the config file.
