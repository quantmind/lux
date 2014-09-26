
Lux is an asynchronous web framework highly extendible and customisable.
Written in python and javascript.

.. _requirements:

Python Requirements
=======================

* pulsar_
* dateutil_


Developing with lux.js
==========================

First you need to install nodejs_ and  grunt_ cli::

    npm install -g grunt-cli

Subsequently install the development packages via::

    npm install

To compile ``lux.js`` use grunt:

    grunt


Angular templates are compiled into javascript via the `grunt-html2js`_ package.


Running Tests & example site
===============================

To run tests and the example site add a new ``settings.py`` file in the
``example.luxweb`` module. The file can simple have the following code::

    from .config *


.. note::

    Lux is the Latin name for ``light``


.. _pulsar: https://github.com/quantmind/pulsar
.. _dateutil: https://pypi.python.org/pypi/python-dateutil
.. _gruntjs: http://gruntjs.com/
.. _nodejs: http://nodejs.org/
.. _grunt: http://gruntjs.com/
.. _`grunt-html2js`: https://github.com/karlgoldstein/grunt-html2js

