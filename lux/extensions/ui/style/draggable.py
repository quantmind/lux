from .base import *


def add_css(all):
    css = all.css

    css('[draggable=true]',
        _moz_user_select='none',
        _khtml_user_select='none',
        _webkit_user_select='none',
        user_select='none',
        # Required to make elements draggable in old WebKit
        _khtml_user_drag='element',
        _webkit_user_drag='element')

    css('.draggable',
        cursor='move')

    css('.draggable-placeholder',
        Skin(border_width=px(3),
             border_style='dashed'))
