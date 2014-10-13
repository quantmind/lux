'''
Highlight code snippets with highlightjs_

.. _highlightjs: https://highlightjs.org/
'''
import lux
from lux import Parameter
from lux.extensions.ui import *


highlight = '//cdnjs.cloudflare.com/ajax/libs/highlight.js/8.3'


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('CODE_HIGHLIGHT_THEME', 'tomorrow',
                  'highlight.js theme')]


def add_css(all):
    theme = all.config('CODE_HIGHLIGHT_THEME')
    css = all.css
    vars = all.variables

    vars.code.descname.font_size = px(24)

    if theme:
        path = 'http:%s/styles/%s.min.css' % (highlight, theme)
        css('body',
            CssInclude(path))

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
