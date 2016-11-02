
# Writing Extensions

Extension are implemented by subclassing the ``LuxExtension`` class::

    from lux.core import LuxExtension

    class Extension(LuxExtension):
        # Optional version number
        _version = '0.1.0'

        def middleware(self, app):
            ...


The ``middleware`` method is called once only by the application and it
must return an iterable over [WSGI][] middleware or ``None``.


## Events

An :class:`.Extension` can register several callbacks which are invoked at different
points during the application live-span. These callbacks receive as
first positional argument, the :class:`.Application` instance running the web site
and are implemented by adding some of the following methods to your
extension class:


### on_config(*app*)


This is the first event to be fired. It is executed once only after the
:attr:`.Application.config` dictionary has been loaded from
the setting file. This is a chance to perform post processing on
parameters before the wsgi :attr:`.Application.handler` is loaded.


### on_loaded(*app*)

.. py:method:: Extension.on_loaded(self, app)

Called once only when all :class:`.Extension` have loaded their
:meth:`~.Extension.middleware` into
the WSGI ``handler``. A chance to add additional middleware or perform
any sort of post-processing on the wsgi application ``handler``.


### on_start(*app*, *server*)

Called once only just before the pulsar ``server`` is about to start serving
the ``app``.


### on_html_document(*app*, *request*, *doc*)

Called the first time the ``request.html_document`` attribute is accessed.
A chance to add static data or any other Html specific information.


### on_form(*app*, *form*)


### on_close(*app*)


[WSGI]: http://www.python.org/dev/peps/pep-3333/
