from lux.extensions.ui.lib import *


def add_css(all):
    css = all.css
    media = all.media
    admin = all.variables.admin

    admin.size = px(250)
    admin.margin_top = px(51)
    admin.min_width_collapse = px(768)
    admin.default.background = '#fff'
    admin.sidebar.default.background = '#F8F8F8'
    admin.sidebar.default.border = '#E7E7E7'

    css('#admin',
        width=pc(100))

    css('.navbar.admin',
        css(' > ul li',
            display='inline-block'),
        margin_bottom=0)

    css('#page-admin',
        padding=spacing(0, 20))

    media(min_width=admin.min_width_collapse).css('#page-admin',
        margin=spacing(0, 0, 0, admin.size),
        min_height=px(1300))

    media(min_width=admin.min_width_collapse).css('.admin-nav',
        margin_top=admin.margin_top,
        position='absolute',
        width=admin.size,
        z_index=1)

    media(max_height=px(600), max_width=px(767)).css('.sidebar-collapse',
        max_height=px(300),
        overflow_y='scroll')

    media(max_height=px(400), max_width=px(767)).css('.sidebar-collapse',
        max_height=px(200),
        overflow_y='scroll')

    css('.admin-default',
        css(' #page-admin',
            Border('solid', admin.sidebar.default.border, left=px(1)),
            background=admin.default.background),
        background=admin.sidebar.default.background)

    css('.admin-nav',
        css(' ul li',
            Border('solid', '#E7E7E7', bottom=px(1))))

    css('.sidebar-search',
        padding=px(15))
