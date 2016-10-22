=================
Getting Started
=================


Python Requirements
=======================

**Hard requirements**

* pulsar_ asychronous engine
* greenlet_ implicit asynchronous code
* jinja2_ template engine
* pytz_ timezones and countries
* dateutil_ date utilities
* sqlalchemy_ and pulsar-odm_ used by ``lux.extensions.odm``
* pyjwt_ used by some authentication backends

**Soft requirements**

* inflect_ correctly generate plurals, ordinals, indefinite articles; convert numbers to words
* markdown_
* oauthlib_ for ``lux.extensions.oauth``
* premailer_ for rendering email HTML


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

Debugging javascript on Chrome::

    npm run-script debug


.. _asyncio: https://docs.python.org/3/library/asyncio.html
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
.. _premailer: https://github.com/peterbe/premailer
.. _inflect: https://github.com/pwdyson/inflect.py
