.. highlight:: python

highlight
================

**Requirements**: :mod:`lux.extensions.ui`, :mod:`lux.extensions.code`

AngularJs module for code highlighting using highlightjs_. This angular module
should be used in conjunction with the :mod:`lux.extensions.code` extentension.
In your config file add the extension to the list of :setting:`EXTENSIONS` and
specify a theme::

    EXTENSIONS = [
        ...
        'lux.extensions.ui',
        'lux.extensions.code',
        ...
    ]
    CODE_HIGHLIGHT_THEME = 'github'

.. highlight:: html

In Javascript you need to use the ``highlight`` directive on the outermost
element containing code to highlight::

    <div data-highlight>
    ...
    </div>

The ``highlight`` module containing the directive is added to lux modules to include in
the bootstrapping process by the :mod:`lux.extensions.code` extension.


.. _highlightjs: https://highlightjs.org/