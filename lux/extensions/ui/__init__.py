'''User interface for styling HTML5 pages.

To use this extension, add the ``lux.extensions.ui`` entry into the
:setting:`EXTENSIONS` list in your config file.
To add additional ``css`` rules, a user extension module must provide the
``add_css`` function which accept one parameter only, the ``css`` container.
The ``add_css`` function is called when building the css file via the ``style``
command.

**Requires**: :mod:`lux.extensions.base`


Parameters
=============

.. lux_extension:: lux.extensions.ui


.. _ui-style:

Styling
=================

.. automodule:: lux.extensions.ui.style


.. _python-css-tools:

Variables and Symbols
=========================

.. automodule:: lux.extensions.ui.lib.base

Colours
===========

.. automodule:: lux.extensions.ui.lib.colorvar


Mixins
=========================

.. automodule:: lux.extensions.ui.lib.mixins


.. _ui-create-skin:

Creating Skins
=======================

.. automodule:: lux.extensions.ui.lib.skins

'''
import lux
from lux import Parameter

from .lib import *


class Extension(lux.Extension):

    _config = [
        Parameter('ICON_PROVIDER', 'fontawesome', 'Icons provider to use'),
        Parameter('BOOTSTRAP', True, 'Set to true to use twitter bootstrap')]

    def on_html_document(self, app, request, doc):
        if doc.has_default_content_type:
            if app.config['BOOTSTRAP']:
                doc.head.links.append('bootstrap_css')
            icon = app.config['ICON_PROVIDER']
            if icon == 'fontawesome':
                doc.head.links.append('fontawesome')
            doc.data('icon', icon)


def add_css(all):
    css = all.css
    vars = all.variables

    # Helper classes
    vars.push_bottom = '20px !important'

    css('.push-bottom',
        margin_bottom=vars.push_bottom)

    # SKINS
    skins = all.variables.skins
    default = skins.default
    default.background = color('#f7f7f9')

    inverse = skins.inverse
    inverse.background = color('#3d3d3d')

    css(('[ng\:cloak], [ng-cloak], [data-ng-cloak], '
         '[x-ng-cloak], .ng-cloak, .x-ng-cloak'),
        display='none !important')

    css('.form-group .help-block',
        display='none')

    css('.form-group.has-error .help-block.active',
        display='block')

    css('.nav-second-level li a',
        padding_left=px(37))

    # a class for setting the aspect ratio of a container
    # put class <div style="padding-top:75%"></div>
    # follow by <div class="absolute-full"></div>
    # to get a 4:3 aspect ratio
    css('.absolute-full',
        position='absolute',
        top=0, bottom=0)
