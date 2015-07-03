from ..lib import *     # noqa


def add_css(all):
    css = all.css
    vars = all.variables

    vars.block_margin = px(30)

    css('.fullpage',
        height=pc(100),
        min_height=pc(100))

    css('.full-width',
        float='left',
        width=pc(100))

    css('.block',
        margin_bottom=vars.block_margin)

    css('.lazyContainer',
        css(' > .content',
            top=0,
            left=0,
            position='absolute',
            width=pc(100),
            min_height=pc(100)),
        position='relative')
