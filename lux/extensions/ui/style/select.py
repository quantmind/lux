from .base import *


def add_css(all):
    cssv = all.variables
    css = all.css

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

    css('body',
        CssInclude(os.path.join(UI_DIR, 'media', 'select2.css'),
                   location='ui/'))
