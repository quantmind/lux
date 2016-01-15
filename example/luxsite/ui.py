from lux.extensions.ui.lib import *     # noqa


def add_css(all):
    css = all.css
    media = all.media
    vars = all.variables

    vars.font_family = ('"freight-text-pro",Georgia,Cambria,"Times New Roman",'
                        'Times,serif')
    vars.font_size = px(18)
    vars.line_height = 1.5
    vars.color = color(0, 0, 0, 0.8)

    vars.navbar_height = 50
    vars.colors.lux_blue = color('#005A8A')
    vars.colors.lux_yellow = color('#E5C700')
    vars.scroll.background = vars.colors.lux_yellow

    add_classes(all)

    css('.fullpage, .angular-view, body, html',
        height=pc(101),
        min_height=pc(101))

    css('#lux-logo',
        height=px(300))

    media(max_height=px(600)).css(
        '#lux-logo',
        height=px(250))

    media(max_height=px(500)).css(
        '#lux-logo',
        height=px(180))

    media(max_height=px(400)).css(
        '#lux-logo',
        height=px(100))

    css('#top a.navbar-brand',
        css(' img',
            height=px(vars.navbar_height),
            width='auto'),
        padding=0)

    css('#page-header',
        padding_top=px(vars.navbar_height))

    css('#page-main',
        min_height=px(500),
        padding_top=px(20),
        padding_bottom=px(50))

    css('#page-footer',
        background_color=vars.colors.lux_blue,
        color=vars.colors.lux_yellow,
        padding_top=px(20),
        min_height=px(300))

    css('.page-header',
        css('.index-header',
            background_color=vars.colors.lux_blue,
            color=vars.colors.gray_lighter,
            height=pc(100),
            width=pc(100),
            min_height=px(300)),
        padding_top=px(vars.navbar_height),
        margin=0)


def add_classes(all):
    css = all.css

    css('.hover-opacity',
        Opacity(0.5),
        css(':hover', Opacity(1)))

    for w in range(1, 10):
        d = 20*w
        css('.width%d' % d,
            width=px(d))
