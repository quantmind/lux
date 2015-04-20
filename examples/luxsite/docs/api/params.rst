.. _parameters:

===============================
Configuration Parameters
===============================

The configuration file is a python file containing several
:class:`.Parameter` which customise your applications. The configuration file
is located in the directory of the main application (extension)
of the site. Check :ref:`project layout <project-layout>` for more
informations.

This is the full list of available :class:`.Parameter` from all :class:`.Extension`
available in the standard lux distribution.

Core
=====================

.. lux_extension:: lux.core.app
   :classname: Application


Base
=====================

.. lux_extension:: lux.extensions.base


REST
================

.. lux_extension:: lux.extensions.rest


Web design
=====================

.. lux_extension:: lux.extensions.ui


.. _parameters-angular:

AngularJS Integration
========================

.. lux_extension:: lux.extensions.angular


.. _parameters-static:

Static Site
================

.. lux_extension:: lux.extensions.static


.. _parameters-oauth:

OAuth and OGP
================

.. lux_extension:: lux.extensions.oauth


.. _parameters-code:

Code Highlight
================

.. lux_extension:: lux.extensions.code
