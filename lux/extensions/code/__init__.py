'''
Highlight code snippets with highlightjs_.

**Required extensions**: :mod:`lux.extensions.ui`

Usage
=========

Include ``lux.extensions.code`` into the :setting:`EXTENSIONS` list in your
:ref:`config file <parameters>`::

    EXTENSIONS = [
        ...
        'lux.extensions.ui',
        'lux.extensions.code'
        ...
        ]

check the :ref:`code hightlight <jsapi-code>` angular module for more
information.

.. _highlightjs: https://highlightjs.org/
'''
import lux
from lux import Parameter
from lux.extensions.angular import add_ng_modules
from lux.extensions.ui import *     # noqa


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('CODE_HIGHLIGHT_THEME', 'tomorrow',
                  'highlight.js theme')]

    def on_html_document(self, app, request, doc):
        add_ng_modules(doc, ('highlight',))


def add_css(all):
    css = all.css
    vars = all.variables

    vars.code.descname.font_size = px(24)

    katex(all)

    def stylepath():
        return 'http:%s/styles/%s.min.css' % (
            CssLibraries['highlight'], all.config('CODE_HIGHLIGHT_THEME'))

    css('body',
        CssInclude(stylepath))

    css('code.hljs.inline',
        display='inline',
        padding=spacing(2, 4))

    # sphinx docs
    css('dl dd',
        margin_left=px(30))

    css('dl.class dl.method',
        color=vars.color)

    css('dl.class, dl.function',
        css(' > dt > tt.descname',
            font_size=vars.code.descname.font_size),
        css(' dt tt.descname',
            color=vars.color,
            font_weight='bold'),
        css(' dt',
            color='#888',
            font_weight='normal',
            font_size=vars.font_size))


def katex(all):
    css = all.css

    css('.katex-outer',
        display='block',
        margin_left='auto',
        margin_right='auto',
        margin_bottom=px(10))
