.. image:: http://quantmind.github.io/lux/media/luxsite/lux-banner.svg
   :alt: Lux
   :width: 50%

|
|

Lux is a library for developing web applications with Python and javascript frameworks such as AngularJS.

:Master CI: |master-build|_ |coverage-master|
:Dev CI: |dev-build|_ |coverage-dev|
:Documentation: http://quantmind.github.io/lux/
:Downloads: https://pypi.python.org/pypi/lux
:Source: https://github.com/quantmind/lux

.. |master-build| image:: https://img.shields.io/travis/quantmind/lux/master.svg
.. _master-build: http://travis-ci.org/quantmind/lux
.. |dev-build| image:: https://img.shields.io/travis/quantmind/lux/dev.svg
.. _dev-build: http://travis-ci.org/quantmind/lux
.. |coverage-master| image:: https://img.shields.io/coveralls/quantmind/lux/master.svg
  :target: https://coveralls.io/r/quantmind/lux?branch=master
.. |coverage-dev| image:: https://img.shields.io/coveralls/quantmind/lux/dev.svg
  :target: https://coveralls.io/r/quantmind/lux?branch=dev

.. _requirements:

Python Requirements
=======================

**Hard requirements**

* pulsar_
* pytz_
* dateutil_

**Soft requirements**

* sqlalchemy_ and pulsar-odm_ used by ``lux.extensions.odm``
* pyjwt_ used by some authentication backends in ``lux.extensions.rest``
* markdown_

Developing with lux.js
==========================

First you need to install nodejs_ and  grunt_ cli::

    npm install -g grunt-cli

Subsequently install the development packages via::

    npm install

To build lux.js_ use grunt::

    grunt build


Angular templates are compiled into javascript via the `grunt-html2js`_ package.


Testing
==========

For testing postgreSQL create a new role::

    psql
    CREATE ROLE lux WITH PASSWORD 'luxtest';
    ALTER ROLE lux CREATEDB LOGIN;
    CREATE DATABASE luxtests;
    GRANT ALL PRIVILEGES ON DATABASE luxtests to lux;



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
.. _sphinx: http://sphinx-doc.org/
.. _`grunt-html2js`: https://github.com/karlgoldstein/grunt-html2js
.. _lux.js: https://raw.githubusercontent.com/quantmind/lux/master/lux/media/lux/lux.js
