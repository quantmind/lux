# Testing

This document describe the tools available for testing lux applications.
These tools are located in the ``lux.utils.test`` module where you can
find two test classes derived from python ``unittest.TestCase``
class.

## Test Classes

### TestCase

This test class is designed to unit test lux components. It provides a
set of methods useful for web applications.

#### # self.application(**parameters)

Create an application with additional config *parameters*

#### # self.authenticity_token(*doc*)

Return the ``CSRF`` token contained in the HTML document if it exists.

### AppTestCase

This test class is designed to test a single lux application and
exposes the following class properties and methods:

#### # cls.app

The test class application. Created in the ``setUpClass`` method
via the ``cls.create_test_application()`` class method.

#### # cls.client

A ``client`` for the application test class, created via
the ``cls.get_client()`` class method.

#### # cls.config_file

Dotted path to the config file used to setup the application for
the test class.

#### # cls.beforeAll()

Class method invoked at the and of the ``setUpClass`` method.
Database and fixtures are already loaded.
By default **it does nothing**,
override to create class level properties.
It can be asynchronous or not.

#### # cls.create_admin_jwt()

Create the application admin JWT token. It can be asynchronous or not.

#### # cls.get_client()

Create a test client. It is used in the ``setUpClass`` to create
the ``cls.client``. By default it returns:
```python
TestClient(cls.app)
```

## Utilities

### TestClient

The test client used for testing lux applications:
```python
client = TestClient(app)
```


### green

Decorator to run a test function on the application ``green_pool``.
