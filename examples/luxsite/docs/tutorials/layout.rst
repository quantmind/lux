.. _project-layout:

==================
Project Layout
==================

A lux project always defines a folder with the name defining the web
application. Let's say the web site is called ``quasar``, than the
project standard layout::

    - quasar-project
        - quasar
            - media
                - src
                - quasar
            __init__.py
            settings.py
        manage.py
        package.json
        Gruntfile.js
        README.rst


The ``manage.py`` script is the main entry point for the web site and should have
the following structure::

    import lux

    if __name__ == '__main__':
        lux.execute_from_config('quasar.settings')


Lux install an utility script which can be used to setup a project and add
extensions to it::

    luxmake.py startproject quasar

creates your project layout inside the ``quasar`` directory.
