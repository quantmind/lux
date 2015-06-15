from lux.extensions.ui import *     # noqa


def add_css(all):
    css = all.css
    vars = all.variables
    vars.list_image_width = 140
    vars.list_image_xs_height = 150

    css('.media-list > .media',
        css(' > a',
            css(' .post-body',
                margin_left=px(vars.list_image_width+20)),
            css(' h3',
                font_weight='normal',
                color=vars.colors.gray_dark),
            text_decoration='none',
            color=vars.colors.gray))

    css('.post-image',
        width=px(vars.list_image_width),
        max_height=px(vars.list_image_width),
        float='left',
        height='auto')

    css('.post-image-xs',
        max_height=px(vars.list_image_xs_height),
        max_width=pc(90),
        width='auto')

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

    css('table.docutils.field-list th',
        padding=spacing(0, 20, 0, 0))
