'''
Highlight code snippets with highlightjs_

.. _highlightjs: https://highlightjs.org/
'''
import lux
from lux import Parameter
from lux.extensions.ui import CssInclude, spacing
from lux.extensions.angular import ng_modules


highlight = '//cdnjs.cloudflare.com/ajax/libs/highlight.js/8.2'


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
        src = '%s/highlight.min' % highlight
        doc.head.scripts.known_libraries['highlight'] = src


def add_css(all):
    theme = all.config('CODE_HIGHLIGHT_THEME')
    css = all.css

    if theme:
        path = 'http:%s/styles/%s.min.css' % (highlight, theme)
        css('body',
            CssInclude(path))

    css('code.hljs.inline',
        display='inline',
        padding=spacing(2, 4))
