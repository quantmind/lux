from lux.extensions.ui.lib import *

collapse_width = 768


def add_css(all):
    css = all.css
    media = all.media
    admin = all.variables.admin
    skins = all.variables.skins

    min_width_collapse = px(collapse_width)

    default = skins.default
    default.admin_background = '#fff'

    admin.size = px(250)
    admin.nav_height = px(50)
    admin.top_nav_padding = px(15)
    admin.default.background = '#fff'
    admin.sidebar.default.background = '#F8F8F8'
    admin.sidebar.default.border = '#E7E7E7'

    css('.admin',
        css('.admin-default',
            background=default.background),
        width=pc(100))

    # admin page default
    css('.admin-page',
        background=default.admin_background,
        margin=spacing(2*admin.nav_height+1, 0, 0, 0),
        min_height=px(568)),

    # admin page on larger devices
    media(min_width=min_width_collapse).css('.admin-page',
        Border('solid', admin.sidebar.default.border, left=px(1)),
        margin=spacing(admin.nav_height+1, 0, 0, admin.size),
        min_height=px(1300))

    media(min_width=min_width_collapse).css('.admin-nav',
        margin_top=admin.nav_height+1,
        position='absolute',
        width=admin.size,
        z_index=1)

    media(max_height=px(600), max_width=px(767)).css('.sidebar-collapse',
        max_height=px(300),
        overflow_y='scroll')

    media(max_height=px(400), max_width=px(767)).css('.sidebar-collapse',
        max_height=px(200),
        overflow_y='scroll')

    css('.navbar.navbar-admin',
        css(' > ul li',
            display='inline-block'),
        margin_bottom=0)

    css('.navbar-top-links',
        css(' > li > a',
            min_height=admin.nav_height,
            padding=admin.top_nav_padding))

    toggle = 40
    css('.nav.nav-side',
        css(' > li',
            css(' > a.with-children',
                display='inline-block',
                margin_left=px(-toggle-5),
                padding_left=px(toggle+5+15),
                width=pc(100)),
            css(' > a.toggle',
                display='inline-block',
                width=px(toggle)),
            Border('solid', '#E7E7E7', bottom=px(1))))

    css('.sidebar-search',
        padding=px(15))

    css('.admin-main',
        padding=spacing(0, 30))

    css('.ribbon',
        css(' .breadcrumb',
            Radius(0),
            margin_bottom=0,
            background='transparent'),
        css('.default',
            background=skins.default.background),
        css('.inverse',
            background=skins.inverse.background),
        width=pc(100))
