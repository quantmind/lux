.. _writing-extensions:

.. module:: lux.core

====================================
Writing Extensions
====================================

Extension are implemented by subclassing the :class:`.Extension` class::

    import lux

    class MyExtension(lux.Extension):
        # Optional version number
        _version = '0.1.0'

        def middleware(self, app):
            ...


The :meth:`.Extension.middleware` method is called once only
by the :class:`.App` serving the web applications, and it must return an iterable over
WSGI_ middleware or ``None``.


Events
================

An :class:`.Extension` can register several callbacks which are invoked at different
points during the application live-span. These callbacks receive as
first positional argument, the :class:`.App` instance running the web site
and are implemented by adding some of the following methods to your
extension class:

.. _event_on_config:

on_config
~~~~~~~~~~~~~~~~~~

.. py:method:: Extension.on_config(self, app)

This is the first event to be fired. It is executed once only after the
:attr:`.App.config` dictionary has been loaded from
the setting file. This is a chance to perform post processing on
parameters before the wsgi :attr:`.App.handler` is loaded.


.. _event_on_loaded:

on_loaded
~~~~~~~~~~~~~~~~~~

.. py:method:: Extension.on_loaded(self, app)

Called once only when all :class:`.Extension` have loaded their
:meth:`~.Extension.middleware` into
the WSGI ``handler``. A chance to add additional middleware or perform
any sort of post-processing on the wsgi application ``handler``.


.. _event_on_start:

on_start
~~~~~~~~~~~~~~~~~~

.. py:method:: Extension.on_start(self, app, server)

Called once only just before the pulsar ``server`` is about to start serving
the ``app``.


.. _event_on_request:

on_request
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Extension.on_request(self, app, request)

Called when a new ``request`` is received by the :class:`App` instance. This
event occurs before the application loops through the WSGI middleware
to produce the response.


.. _event_on_html_document:

on_html_document
~~~~~~~~~~~~~~~~~~

.. py:method:: Extension.on_html_document(self, app, request, doc)

Called the first time the ``request.html_document`` attribute is accessed.
A chance to add static data or any other Html specific information.


.. _event_on_form:

on_form
~~~~~~~~~~~~~~~~~~

.. py:method:: Extension.on_form(self, app, form)


.. _event_response:

on_html_response
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Extension.on_html_response(self, app, request, html)

Called by the :class:`Html.html_response` method. The ``html`` input
is a dictionary containing the ``body`` keys with the html element
which is being rendered in the body part of the Html page.




 .. _WSGI: http://www.python.org/dev/peps/pep-3333/
