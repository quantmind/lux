# Writing Extensions

Extension are implemented by subclassing the ``LuxExtension`` class::
```python
    from lux.core import LuxExtension

    class Extension(LuxExtension):
        # Optional version number
        _version = '0.1.0'

        def middleware(self, app):
            ...
```

The ``middleware`` method is called once only by the application and it
must return an iterable over [WSGI][] middleware or ``None``.


## Events

An extension can register several callbacks which are invoked at different
points during the application life-span. These callbacks receive as
first positional argument, the application instance running the web site
and are implemented by adding some of the following methods to your
extension class.


### on_config(*app*)

This is the first event to be fired. It is executed once only after the
```app.config``` dictionary has been loaded from
the setting file. This is a chance to perform post processing on
parameters.


### on_loaded(*app*)

Called once only when all extensions have loaded their
middleware into the WSGI handler.
A chance to add additional middleware or perform
any sort of post-processing on the wsgi application ``handler``.


### on_start(*app*, *server*)

Called once only just before the wsgi ``server`` is about to start serving
the ``app``.


### on_html_document(*app*, *request*, *doc*)

Called the first time the ``request.html_document`` attribute is accessed.
A chance to add static data or any other Html specific information.


### on_form(*app*, *form*)


### on_close(*app*)


[WSGI]: http://www.python.org/dev/peps/pep-3333/
