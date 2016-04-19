.. image:: http://quantmind.github.io/lux/media/luxsite/lux-banner.svg
   :alt: Lux
   :width: 50%

|
|

Lux is a library for developing web applications with Python and javascript frameworks such as AngularJS.

:Badges: |license|  |pyversions| |status| |downloads|
:Master CI: |master-build| |coverage-master|
:Dev CI: |dev-build| |coverage-dev|
:Javascript: |jsdep| |jsdevdep|
:Documentation: http://quantmind.github.io/lux/
:Downloads: https://pypi.python.org/pypi/lux
:Source: https://github.com/quantmind/lux
:Design by: `Quantmind`_
:Platforms: Linux, OSX, Windows. Python 3.5 and above
:Keywords: asynchronous, wsgi, websocket, redis, json-rpc, REST, web

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/lux.svg
  :target: https://pypi.python.org/pypi/lux
.. |license| image:: https://img.shields.io/pypi/l/lux.svg
  :target: https://pypi.python.org/pypi/lux
.. |status| image:: https://img.shields.io/pypi/status/lux.svg
  :target: https://pypi.python.org/pypi/v
.. |downloads| image:: https://img.shields.io/pypi/dd/lux.svg
  :target: https://pypi.python.org/pypi/lux
.. |master-build| image:: https://img.shields.io/travis/quantmind/lux/master.svg
  :target: http://travis-ci.org/quantmind/lux
.. |dev-build| image:: https://img.shields.io/travis/quantmind/lux/dev.svg
  :target: http://travis-ci.org/quantmind/lux
.. |coverage-master| image:: https://img.shields.io/coveralls/quantmind/lux/master.svg
  :target: https://coveralls.io/r/quantmind/lux?branch=master
.. |coverage-dev| image:: https://img.shields.io/coveralls/quantmind/lux/dev.svg
  :target: https://coveralls.io/r/quantmind/lux?branch=dev
.. |jsdep| image:: https://david-dm.org/quantmind/lux.svg?path=example
  :target: https://david-dm.org/quantmind/lux
.. |jsdevdep| image:: https://david-dm.org/quantmind/lux/dev-status.svg?path=example
  :target: https://david-dm.org/quantmind/lux#info=devDependencies

.. _requirements:

Python Requirements
=======================

**Hard requirements**

* pulsar_ asychronous engine
* greenlet_ implicit asynchronous code
* jinja2_ template engine
* pytz_ timzones and countries
* dateutil_ date utilities

**Soft requirements**

* sqlalchemy_, greenlet_ and pulsar-odm_ used by ``lux.extensions.odm``
* pyjwt_ used by some authentication backends in ``lux.extensions.rest``
* markdown_
* oauthlib_ for ``lux.extensions.oauth``


Testing
==========

For testing, create the test database first::

    psql -a -f tests/db.sql

To run tests::

    python setup.py test

For options and help type::

    python setup.py test --help

flake8_ check (requires flake8 package)::

    flake8


.. _pulsar: https://github.com/quantmind/pulsar
.. _pytz: http://pytz.sourceforge.net/
.. _dateutil: https://pypi.python.org/pypi/python-dateutil
.. _sqlalchemy: http://www.sqlalchemy.org/
.. _pulsar-odm: https://github.com/quantmind/pulsar-odm
.. _pyjwt: https://github.com/jpadilla/pyjwt
.. _pbkdf2: https://pypi.python.org/pypi/pbkdf2
.. _gruntjs: http://gruntjs.com/
.. _nodejs: http://nodejs.org/
.. _grunt: http://gruntjs.com/
.. _markdown: https://pypi.python.org/pypi/Markdown
.. _oauthlib: https://oauthlib.readthedocs.org/en/latest/
.. _sphinx: http://sphinx-doc.org/
.. _greenlet: https://greenlet.readthedocs.org
.. _`grunt-html2js`: https://github.com/karlgoldstein/grunt-html2js
.. _lux.js: https://raw.githubusercontent.com/quantmind/lux/master/lux/media/lux/lux.js
.. _`Quantmind`: http://quantmind.com
.. _flake8: https://pypi.python.org/pypi/flake8
.. _jinja2: http://jinja.pocoo.org/docs/dev/
