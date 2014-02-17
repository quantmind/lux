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


class Extension(lux.Extension):
    attributions = ['Font Awesome by Dave Gandy - '
                    'http://fortawesome.github.com/Font-Awesome']

    _config = [
        Parameter('THEME', None, ''),
        Parameter('ICON_PROVIDER', 'fontawesome', 'Icons used')]

    def on_html_document(self, app, request, html):
        icon = app.config['ICON_PROVIDER']
        if icon == 'fontawesom':
            html.head.links.append({'all':
                                    [('ui/font-awesome-ie7.min.css', 'IE 7')]})
        html.data('icon', icon)


class Tabs(lux.Html):
    def __init__(self, *children, **params):
        super(Tabs, self).__init__('div', *children, **params)
        self.addClass('tabs')

    def append(self, child):
        if isinstance(child, (list, tuple)):
            # must be of length 2
            if len(child) != 2:
                raise TypeError('Adding wrong type to tabs. Required a string'
                                ' or a two element tuple. Got a %s elements'
                                % len(child))
            a, div = child
        else:
            # when a string set the div to empty string
            a, div = child, ''
        if not self.children:
            ul = lux.Html('ul')
            self.children.append(ul)
        a = lux.as_tag(a, 'a')
        if not a.attr('href'):
            count = len(self.children[0].children) + 1
            id = 'tabs-%s' % count
            a.attr('href', '#%s' % id)
            div = lux.as_tag(div, 'div').attr('id', id)
        self.children[0].append(a)
        if div:
            self.children.append(div)
