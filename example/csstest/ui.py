from lux.extensions.ui.lib import *


def add_css(all):
    css = all.css
    cssv = all.variables

    css('.lux-example',
        css(':after',
            Radius(spacing(cssv.body.radius, 0)),
            Border('#DDDDDD'),
            background='#F5F5F5',
            color='#9DA0A4',
            content='"Example"',
            font_size=px(12),
            font_weight='bold',
            padding=spacing(3, 7),
            position='absolute',
            left='-1px',
            top='-1px'),
        Radius(cssv.body.radius),
        Skin(only='default', gradient=lambda g: g.start),
        padding=spacing(39, 19, 14),
        margin=spacing(15, 0),
        position='relative')

    css('.lux-example + .prettyprint',
        margin_top=px(-20),
        padding_top=px(15))
