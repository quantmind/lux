# Application

This document describe the public API of a Lux Application ``app``.
The application is an [asynchrouns WSGI][] handler.

## app

The application itself:
```python
app == app.app
```
Useful when using the applicatin instead of a ``request`` object

## callable

Instance of the ``App`` class which created the application. The callable
is a picklable object and thereofre it can be passed to subprocesses when
running in multiprocessing mode.
```python
app == app.callable.handler()
```

The callable exposes the following properties:

* ``app.callable.command`` name of the command executed
* ``app.callable.argv`` list or command line parameters, without the command name 
* ``app.callable.script`` the python script which created the application


## forms

Dictionary of forms available

## green_pool

Pool of greenlets where middleware are executed

## stdout & stderr

Application standard output and standard error

[asynchrouns WSGI]: http://quantmind.github.io/pulsar/apps/wsgi/async.html
