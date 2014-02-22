from .base import *


requires = ['base']


def add_css(all):
    cssv = all.variables
    css = all.css
    #
    cssv.well.radius = cssv.body.radius
    cssv.panel.radius = cssv.body.radius
    cssv.panel.padding = px(9)
    #
    css('.well',
        css('.well-sm',
            Radius(0.6*cssv.well.radius),
            padding=px(9)),
        css('.well-lg',
            Radius(1.2*cssv.well.radius),
            padding=px(24)),
        Shadow(0, px(1), px(1), color=RGBA(0,0,0,0.05), inset=True),
        Radius(cssv.well.radius),
        background=as_value(cssv.skins.default.active.background).start,
        min_height=px(20),
        padding=px(19))

    #
    css('.panel',
        Radius(cssv.panel.radius),
        Skin(applyto=['border']),
             Radius(cssv.panel.radius),
             Skin(' .header', border_width=spacing(0, 0, px(1))),
        css(' .header',
            Radius(spacing(cssv.panel.radius, cssv.panel.radius, 0, 0)),
            padding=cssv.panel.padding),
        css(' .body',
            padding=cssv.panel.padding))
