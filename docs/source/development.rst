==================
Development
==================

To develop lux or lux -based applications there are additional requirements:

* gruntjs_ and therefore nodejs_::

    npm install -g grunt-cli

  will install the grunt command line. Then on the ``lux`` distribution
  directory type::

    npm install

  to locally install ``grunt` and the other javascript libraries used
  during development (specified in ``package.json``).


Documentation
====================

To build the documentation one needs sphinx_ and docco_ for the javascript code.
Before compiling the documentation you need to create the ``docs/lux/html``
directory one level up from the package directory::

    - lux
        - docs
        - lux
        ...
    - docs
        - lux
            - html
                - docco

from within the ``lux/docs`` directory type::

    make html

To build the javascript documents, from the ``lux`` directory type::

    grunt docco


Testing
======================

To test Lux

* Create a ``test_settings.py`` in the distribution directory and add the
  various API ids and secret keys.
