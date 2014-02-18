from lux.extensions.ui.lib import *


def add_css(all):
    cssv = all.variables
    classes = all.classes
    css = all.css
    #
    cssv.navbar.padding = spacing(6, 15)
    cssv.navbar.line_height = cssv.body.line_height
    #
    cssv.navbar.brand.font_size = px(18)
    #
    cssv.tabs.padding = cssv.button.padding
    cssv.tabs.background = cssv.body.background
    cssv.tabs.color = cssv.body.color
    cssv.tabs.margin = px(5)

    css('.navbar',
        Skin(only=('default', 'inverse')),
        Skin(' li > a',
             only=('default', 'inverse'), clickable=True,
             applyto=('background', 'color',)),
        Skin(' .brand',
             only=('default', 'inverse'), clickable=True,
             applyto=('color',)),
        css(' .nav',
            css('.secondary',
                float='right'),
            css('.user',
                float='right'),
            css(' > li',
                css(' > a',
                    float='none',
                    padding=cssv.navbar.padding),
                float='left'),
            display='block',
            float='left',
            margin=spacing(0, 10, 0, 0),
            position='relative'),
        css(' .brand',
            max_width='none',
            display='block',
            float='left',
            text_decoration='none',
            line_height=cssv.navbar.line_height,
            padding=cssv.navbar.padding,
            font_size=cssv.navbar.brand.font_size),
        overflow='visible')