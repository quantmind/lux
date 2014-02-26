from lux.extensions.ui.lib import *


def add_css(all):
    cssv = all.variables
    css = all.css
    #
    css('.lux-example',
        Radius(cssv.body.radius, 'top'),
        Skin(only='default', border_width=px(1)),
        css(':after',
            color=color(cssv.skins.default.default.color, alpha=0.3),
            content='"Example"',
            font_size=px(12),
            font_weight=700,
            left=px(15),
            letter_spacing=px(1),
            position='absolute',
            text_transform='uppercase',
            top=px(15)),
        css(' + .highlight',
            margin_top=px(-16)),
        padding=spacing(45, 15, 15),
        position='relative',
        margin_bottom=px(15))

    css('.highlight',
        Skin(only='default', border_width=px(1)),
        Radius(cssv.body.radius, 'bottom'),
        margin_bottom=px(15))
