from lux.extensions.ui.lib import *


def add_css(all):
    css = all.css

    css('#page-header',
        min_height=px(60))

    css('#page-main',
        min_height=px(500))

    css('#page-footer',
        Skin(only='default', noclass='default'),
        Border(top=px(1)),
        min_height=px(200))
