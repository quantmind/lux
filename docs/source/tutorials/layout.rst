.. _project-layout:

==================
Project Layout
==================

A lux project always defines a folder with the name defining the web
application. Let's say the web site is called ``quasar``, than the
project standard layout::

    - project-folder
        - app1
            __init__.py
        - quasar
            __init__.py
            config.py
        manage.py
        grunt.js


The ``manage.py`` script is the main entry point for the web site and should have
the following structure::

    import lux

    if __name__ == '__main__':
        lux.execute_from_config('quasar.config')


Lux install an utility script which can be used to setup a project and add
extensions to it::

    luxmake.py createproject quasar

creates your project layout inside the ``quasar`` directory.

The Config Script
========================

The configuration script is where your application settings are defined.



