'''Extension for creating style sheets using python. It provides
the :ref:`style command <style-command>` but no WSGI middleware.

To use this extension, add the ``lux.extensions.ui`` entry into the
:setting:`EXTENSIONS` list in your config file.
To add additional ``css`` rules, a user extension module must provide the
``add_css`` function which accept one parameter only, the ``css`` container.
The ``add_css`` function is called when building the css file via the ``style``
command.

Usage
=======

The API is quite simple::

    import lux
    from lux.extensions.ui import *

    class Extension(lux.Extension):
        "An extension class must be defined"


    def add_css(root):
        css = root.css

        css('.myelement',
            Border(color='#333', width=px(1)),
            max_width=px(400))

The ``root`` element is the container of all css rules (effectively it
is the css file) and it is an instance of the :class:`.Css` class::

    from lux.extensions.ui import Css

    root = Css()

The :class:`.Border` in the example is a :class:`.Mixin` which generate
css border rules for the css element where it is declared. The ``max_width``
key-valued pair is added to the css rules too. When the python code
is converted into stylesheets, all underscore (``_``) are converted into
dashes (``-``).

.. _style-command:

The style Command
=====================

This extension provide the ``style`` command for creating the css file of your
web application::

    python manage.py style --minify


.. _python-css-tools:

Variables and Symbols
=========================

.. automodule:: lux.extensions.ui.lib.base
   :members:
   :member-order: bysource

Colours
===========

.. automodule:: lux.extensions.ui.lib.colorvar
   :members:
   :member-order: bysource

Mixins
=========================

.. automodule:: lux.extensions.ui.lib.mixins
   :members:
   :member-order: bysource

'''
import lux
from lux import Parameter

from .lib import *              # noqa
from .libs import CssLibraries  # noqa
from .css import add_css        # noqa


class Extension(lux.Extension):

    _config = [
        Parameter('EXCLUDE_EXTENSIONS_CSS', None,
                  'Optional list of extensions to exclude form the css'),
        Parameter('NAVBAR_COLLAPSE_WIDTH', 768,
                  'Width when to collapse the navbar')]

    def on_html_document(self, app, request, doc):
        navbar = doc.jscontext.get('navbar') or {}
        navbar['collapseWidth'] = app.config['NAVBAR_COLLAPSE_WIDTH']
        doc.jscontext['navbar'] = navbar
