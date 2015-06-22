from ..lib import *     # noqa


def add_css(all):
    css = all.css
    vars = all.variables

    css('.fullpage',
        height=pc(100),
        min_height=pc(100))

    css('.full-width',
        float='left',
        width=pc(100))

    css('.push-bottom',
        margin_bottom=vars.push_bottom)

    css('.lazyContainer',
        css(' > .content',
            top=0,
            left=0,
            position='absolute',
            width=pc(100),
            min_height=pc(100)),
        position='relative')
