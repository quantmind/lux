from lux.extensions.ui import *


def add_css(all):
    css = all.css

    css('.dir-entry-image',
        css(' img',
            width=px(120),
            height='auto'),
        overflow='hidden',
        max_height=px(90))

    sphinx(all)


def sphinx(all):
    css = all.css
    vars = all.variables

    vars.headerlink.color = vars.colors.gray_lighter
    vars.headerlink.color_hover = vars.colors.gray_light

    for n in range(1, 7):
        css('h%d:hover > a.headerlink' % n,
            visibility='visible')
    css('dt:hover > a.headerlink', visibility='visible')

    css('a.headerlink',
        css(':hover',
            color=vars.headerlink.color_hover),
        padding=spacing(0, 4),
        color=vars.headerlink.color,
        text_decoration='none',
        visibility='hidden')

    css('.viewcode-link',
        float='right')

    css('div.viewcode-block:target',
        margin=spacing(-1, -10),
        padding=spacing(0, 10))
