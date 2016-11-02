# Application

This document describe the public API of a Lux Application. The application
is an [asynchrouns WSGI][] handler.

## callable

Instance of the ``App`` class which created the application. The callable
is a picklable object and thereofre it can be passed to subprocesses when
running in multiprocessing mode.
```
app == app.callable.handler()
```

The callable exposes the following properties:

* ``app.callable.`


## forms

Dictionary of forms available


[asynchrouns WSGI]: http://quantmind.github.io/pulsar/apps/wsgi/async.html
