'''Styling for select2 jQuery plugin
'''
import lux

from .base import *


def add_css(all):
    select = lux.javascript_libraries.get('select')
    url = None
    if select:
        bits = select.split('/')
        if bits[-1] == 'select2.js':
            bits[-1] = 'select2.css'
            url = '/'.join(bits)
            if not url.startswith('http'):
                url = 'http:%s' % url

    cssv = all.variables
    css = all.css

    if url:
        css('body',
            CssInclude(url, location='ui/'))

    def select_height():
        p = as_value(cssv.input.padding)
        l = as_value(cssv.body.line_height)
        return l + p.top + p.bottom + px(2)

    def select_width():
        p = as_value(cssv.input.padding)
        l = as_value(cssv.input.width)
        return l + p.left + p.right + px(2)

    css('select',
        line_height=Lazy(select_height),
        height=Lazy(select_height),
        width=Lazy(select_width))

    css('select[multiple], select[size]',
        height='auto')
