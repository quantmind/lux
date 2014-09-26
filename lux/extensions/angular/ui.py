from lux.extensions.ui.lib import *


def add_css(all):
    css = all.css
    collapse_width = all.app.config['NAVBAR_COLLAPSE_WIDTH']
    media = all.media
    navbar = all.variables.navbar
    sidebar = all.variables.sidebar
    #
    skins = all.variables.skins

    min_width_collapse = px(collapse_width)

    sidebar.width = px(250)
    navbar.height = px(50)

    media(min_width=min_width_collapse).css('.admin-nav',
        margin_top=navbar.height+1,
        position='absolute',
        width=sidebar.width,
        z_index=1)

    media(max_height=px(600), max_width=px(767)).css('.sidebar-collapse',
        max_height=px(300),
        overflow_y='scroll')

    media(max_height=px(400), max_width=px(767)).css('.sidebar-collapse',
        max_height=px(200),
        overflow_y='scroll')
