from .base import *


def add_css(all):
    cssv = all.variables
    css = all.css
    #
    cssv.well.radius = cssv.body.radius
    #
    css('.well',
        css('.well-sm',
            Radius(0.6*cssv.well.radius),
            padding=px(9)),
        css('.well-lg',
            Radius(1.2*cssv.well.radius),
            padding=px(24)),
        Skin(exclude=('base', 'zen', 'zen-dark'),
             gradient=False),
        Shadow(0, px(1), px(1), color=RGBA(0,0,0,0.05), inset=True),
        Radius(cssv.well.radius),
        min_height=px(20),
        padding=px(19))
