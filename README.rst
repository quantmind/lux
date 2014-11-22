.. image:: http://quantmind.github.io/lux/media/luxsite/lux-banner.png
   :alt: Lux
   :width: 90%


Lux is a library for developing web applications with Python and AngularJS.

.. _requirements:

Python Requirements
=======================

* pulsar_
* dateutil_

Additionally, Lux can benefit form these python libraries

* markdown_
* sphinx_

Developing with lux.js
==========================

First you need to install nodejs_ and  grunt_ cli::

    npm install -g grunt-cli

Subsequently install the development packages via::

    npm install

To build lux.js_ use grunt::

    grunt build


Angular templates are compiled into javascript via the `grunt-html2js`_ package.


.. _pulsar: https://github.com/quantmind/pulsar
.. _dateutil: https://pypi.python.org/pypi/python-dateutil
.. _gruntjs: http://gruntjs.com/
.. _nodejs: http://nodejs.org/
.. _grunt: http://gruntjs.com/
.. _markdown: https://pypi.python.org/pypi/Markdown
.. _sphinx: http://sphinx-doc.org/
.. _`grunt-html2js`: https://github.com/karlgoldstein/grunt-html2js
.. _lux.js: https://raw.githubusercontent.com/quantmind/lux/master/lux/media/lux/lux.js

