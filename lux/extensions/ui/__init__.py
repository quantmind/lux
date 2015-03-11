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

from .css import *
from .lib import *


class Extension(lux.Extension):

    _config = [
        Parameter(
            'FONTAWESOME',
            '//netdna.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome',
            'FONTAWESOME url. Set to none to not use it.'),
        Parameter(
            'BOOTSTRAP',
            '//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap',
            'Twitter bootstrap url. Set to none to not use it.'),
        Parameter('EXCLUDE_EXTENSIONS_CSS', None,
                  'Optional list of extensions to exclude form the css'),
        Parameter('NAVBAR_COLLAPSE_WIDTH', 768,
                  'Width when to collapse the navbar')]

    def on_html_document(self, app, request, doc):
        navbar = doc.jscontext.get('navbar') or {}
        navbar['collapseWidth'] = app.config['NAVBAR_COLLAPSE_WIDTH']
        doc.jscontext['navbar'] = navbar
        for name in ('BOOTSTRAP', 'FONTAWESOME'):
            doc.head.links.append(app.config[name])


def add_css(all):
    css = all.css
    vars = all.variables

    vars.font_family = '"Helvetica Neue",Helvetica,Arial,sans-serif'
    vars.font_size = px(14)
    vars.line_height = 1.42857
    vars.font_style = 'normal'
    vars.color = color('#333')
    vars.background = color('#fff')
    # Helper classes
    vars.push_bottom = '20px !important'

    black = color('#000')
    vars.colors.gray_darker = lighten(black, 13.5)
    vars.colors.gray_dark = lighten(black, 20)
    vars.colors.gray = lighten(black, 50)
    vars.colors.gray_light = lighten(black, 70)
    vars.colors.gray_lighter = lighten(black, 93.5)

    # SKINS
    skins = vars.skins
    default = skins.default
    default.background = color('#f7f7f9')

    inverse = skins.inverse
    inverse.background = color('#3d3d3d')

    css('body',
        font_family=vars.font_family,
        font_size=vars.font_size,
        line_height=vars.line_height,
        font_style=vars.font_style,
        background=vars.background,
        color=vars.color)

    classes(all)
    anchor(all)
    add_navbar(all)

    css('p.form-error',
        margin=0)

    css('.form-group .help-block',
        display='none')

    css('.form-group.has-error .help-block.active',
        display='block')

    css('.nav-second-level li a',
        padding_left=px(37))

    css('.nav.navbar-nav > li > a',
        outline='none')


def classes(all):
    css = all.css
    vars = all.variables

    css('.fullpage',
        height=pc(100),
        min_height=pc(100))

    css('.push-bottom',
        margin_bottom=vars.push_bottom)

    css('.lazyContainer',
        css(' > .content',
            top=0,
            left=0,
            position='absolute',
            width=pc(100),
            min_height=pc(100)),
        position='relative')


def anchor(all):
    '''Both ``anchor.color`` and ``anchor.color_hover`` variables are
    left unspecified so that this rule only apply when an set their
    values
    '''
    css = all.css
    vars = all.variables

    vars.anchor.color = None
    vars.anchor.color_hover = None

    css('a',
        css(':hover',
            color=vars.anchor.color_hover),
        color=vars.anchor.color)


def add_navbar(all):
    '''
    The navbar2 page layout should use the following template::

        <navbar2>
            ...
        </navbar2>
    '''
    css = all.css
    cfg = all.app.config
    media = all.media
    vars = all.variables
    #
    # STYLING
    navbar = vars.navbar
    navbar.default.background = '#f8f8f8'
    #
    # NAVBAR (TOP)
    navbar.height = px(50)
    #
    # SIDEBAR
    sidebar = vars.sidebar
    sidebar.default.border = '#E7E7E7'
    sidebar.width = px(250)
    min_width_collapse = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    css('.navbar',
        css(' .navbar-toggle',
            margin_top=0.5*(navbar.height-50)+8),
        min_height=navbar.height)

    css('.navbar-default',
        background=navbar.default.background)

    # wraps the navbar2 and the main page
    css('.navbar2-wrapper',
        css(' > .navbar', margin_bottom=0),
        width=pc(100),
        min_height=pc(100))

    css('.navbar2-page',
        background=vars.background,
        padding=spacing(15, 15, 0))

    media(min_width=min_width_collapse).css(
        '.navbar2-page',
        margin=spacing(0, 0, 0, sidebar.width)).css(
        '.navbar2-wrapper.navbar-default .navbar2-page',
        Border(color=sidebar.default.border, left=px(1)))

    media(min_width=min_width_collapse).css(
        '.sidebar',
        margin_top=navbar.height+1,
        position='absolute',
        width=sidebar.width,
        z_index=1)
