.. image:: http://quantmind.github.io/lux/media/luxsite/lux-banner.png
   :alt: Lux
   :width: 50%

Lux is a library for developing web applications with Python and AngularJS.

.. _requirements:

Python Requirements
=======================

**Hard requirements**

* pulsar_
* pytz_
* dateutil_

**Soft requirements**

* sqlalchemy_ used by ``lux.extensions.odm``
* markdown_ used by ``lux.extensions.static``
* sphinx_ used by ``lux.extensions.static``
* pyjwt_ used by some authentication backends in ``lux.extensions.rest``

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

    CREATE ROLE lux WITH PASSWORD 'luxtest';
    ALTER ROLE lux CREATEDB;
    CREATE DATABASE luxtests;
    GRANT ALL PRIVILEGES ON DATABASE luxtests to lux;



.. _pulsar: https://github.com/quantmind/pulsar
.. _pytz: http://pytz.sourceforge.net/
.. _dateutil: https://pypi.python.org/pypi/python-dateutil
.. _sqlalchemy: http://www.sqlalchemy.org/
.. _pyjwt: https://github.com/jpadilla/pyjwt
.. _gruntjs: http://gruntjs.com/
.. _nodejs: http://nodejs.org/
.. _grunt: http://gruntjs.com/
.. _markdown: https://pypi.python.org/pypi/Markdown
.. _sphinx: http://sphinx-doc.org/
.. _`grunt-html2js`: https://github.com/karlgoldstein/grunt-html2js
.. _lux.js: https://raw.githubusercontent.com/quantmind/lux/master/lux/media/lux/lux.js

