from .base import *


def add_css(all):
    cssv = all.variables
    css = all.css
    #
    cssv.dialog.background = cssv.skins.base.default.background
    cssv.dialog.backdrop.background = '#000'
    cssv.dialog.backdrop.opacity = 0.5
    cssv.dialog.radius = cssv.body.radius
    cssv.dialog.line_height = px(24)
    cssv.dialog.padding = px(10)

    # collapse
    css('.collapse',
        Transition('height', '0.35s', 'ease'),
        css('.in', height='auto'),
        position='relative',
        overflow='hidden',
        height=0)

    css('.header',
        css(' h3',
            line_height=cssv.dialog.line_height,
            margin=0),
        overflow='hidden')

    css('.body-wrap',
        position='relative',
        overflow='hidden')

    css('.body',
        position='relative',
        overflow_y='auto')

    dialog = css('.dialog',
                 Opacity(0),
                 Skin(applyto=['border']),
                 Skin(' .header', border_width=spacing(0, 0, px(1))),
                 Radius(cssv.dialog.radius),
                 Transition('opacity', '0.2s', 'ease'),
                 css('.ready',
                     Opacity(1),
                     css('.collapsed',
                         css(' .header', Radius(cssv.dialog.radius)),
                         # Remove border from header
                         Skin(' .header',
                              applyto=['border'],
                              border_style='none'))))

    # control variant
    dialog.css('.ready',
               Skin('.control', applyto=['border'], border_style='none'),
               Skin('.control > .header',
                    applyto=['border'],
                    border_style='none'),
               css('.control',
                   Radius(0),
                   css(' > .header',
                       Radius(0),
                       padding=0)))

    css('.modal-backdrop',
        Opacity(cssv.dialog.backdrop.opacity),
        background=cssv.dialog.backdrop.background)

    ##    DIALOG
    dialog.css(' .header',
               Radius(spacing(cssv.dialog.radius, cssv.dialog.radius, 0, 0)),
               padding=spacing(0.6*cssv.dialog.padding, cssv.dialog.padding))

    dialog.css(' .body',
               Radius(spacing(0, 0, cssv.dialog.radius, cssv.dialog.radius)),
               background=cssv.dialog.background,
               padding=cssv.dialog.padding)
