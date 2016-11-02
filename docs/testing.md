# Testing

This document describe the tools available for testing lux applications.
These tools are located in the ``lux.utils.test`` module where you can
find two test classes derived from python ``unittest.TestCase``
class.

## Test Classes

### test.TestCase

This test class is designed to unit test lux components. It provides a
set of methods useful for web applications.

#### test.authenticity_token(*doc*)

Return the ``CSRF`` token contained in the HTML document if it exists.

### test.AppTestCase

This test class is designed to test a single lux application and
exposes the following class properties and methods:

#### testcls.client

A ``client`` for the application test class, created via
the ``testcls.get_client()`` class method.

#### testcls.config

Dotted path to the config file used to setup the application for
the test class

#### testcls.create_admin_jwt()

Create the application admin JWT token

## Utilities

### TestClient

The test client usid for testing lux applications:
```python
client = TestClient(app)
```


### green

Decorator to run a test function on the application ``green_pool``.
