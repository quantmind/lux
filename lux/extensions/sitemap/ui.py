from lux.extensions.ui.lib import *


def add_css(all):
    cssv = all.variables
    classes = all.classes
    css = all.css
    #
    cssv.navbar.padding = spacing(6, 15)
    cssv.navbar.line_height = cssv.body.line_height
    #
    cssv.navbar.brand.font_size = px(18)
    #
    cssv.tabs.padding = cssv.button.padding
    cssv.tabs.background = cssv.body.background
    cssv.tabs.color = cssv.body.color
    cssv.tabs.margin = px(5)

    css('.navbar',
        Skin(only=('default', 'inverse')),
        Skin(' li > a',
             only=('default', 'inverse'), clickable=True,
             applyto=('background', 'color',)),
        Skin(' .brand',
             only=('default', 'inverse'), clickable=True,
             applyto=('color',)),
        css(' .nav',
            css('.secondary',
                float='right'),
            css('.user',
                float='right'),
            css(' > li',
                css(' > a',
                    float='none',
                    padding=cssv.navbar.padding),
                float='left'),
            display='block',
            float='left',
            margin=spacing(0, 10, 0, 0),
            position='relative'),
        css(' .brand',
            max_width='none',
            display='block',
            float='left',
            text_decoration='none',
            line_height=cssv.navbar.line_height,
            padding=cssv.navbar.padding,
            font_size=cssv.navbar.brand.font_size),
        overflow='visible')

    css('.nav',
        Clearfix(),
        css('a',
            text_decoration='none'),
        css(' > li > a',
            display='block'),
        list_style='none outside none',
        padding=px(0),
        margin=px(0))

    #nav-tabs
    css('.nav-tabs',
        css(' > li',
            css(' > a',
                Skin(clickable=True, exclude='base'),
                line_height=px(20),
                padding=spacing(8, 14)),
            margin_bottom=px(-1)))

    #css('.nav-list',
    #    Skin('> li > a', clickable=True),
    #    css('> li > a',
    #        display='block',
    #        padding=spacing(4, 15),
    #        margin=spacing(0, 0, '-1px')))


def add_tabs(all):
    css('.tabs',
        Skin('.tabs-top > ul', border_width=spacing(0, 0, 1),
             background=False),
        Skin('.tabs-bottom > ul', border_width=spacing(1, 0, 0),
             background=False),
        Skin('.tabs-left > ul', border_width=spacing(0, 1, 0, 0),
             background=False),
        Skin('.tabs-right > ul', border_width=spacing(0, 0, 0, 1),
             background=False),
        Skin('> ul > li > a', clickable=True,
             active={'background': cssv.tabs.background,
                     'color': cssv.tabs.color}),
        css('.tabs-top > ul > li > a.active.open',
            border_bottom_color=cssv.tabs.background),
        css(' .content',
            overflow='auto',
            padding=cssv.tabs.margin),
        css('> ul',
            Clearfix(),
            css('> li',
                css('> a',
                    display='block',
                    padding=cssv.tabs.padding),
                background='inherit'),
            background='inherit'),
        css('.tabs-top',
            css('> ul',
                css('> li',
                    css('> a',
                        Radius(spacing(cssv.body.radius,
                                       cssv.body.radius, 0, 0)),
                        margin_right=cssv.tabs.margin),
                    margin_bottom='-1px',
                    float='left'),
                padding=spacing(cssv.tabs.margin, cssv.tabs.margin, 0))),
        css('.tabs-bottom',
            css('> ul',
                css('> li',
                    css('> a',
                        Radius(spacing(0, 0, cssv.body.radius,
                                       cssv.body.radius)),
                        margin_right=cssv.tabs.margin),
                    margin_top='-1px',
                    float='left'),
                padding=spacing(0, cssv.tabs.margin, cssv.tabs.margin))),
        css('.tabs-left',
            css('> ul',
                css('> li',
                    css('> a',
                        Radius(spacing(cssv.body.radius, 0, 0,
                                       cssv.body.radius)),
                        margin_bottom=cssv.tabs.margin),
                    margin_right='-1px'),
                padding=spacing(cssv.tabs.margin, 0, 0, cssv.tabs.margin),
                float='left')),
        css('.tabs-right',
            css('> ul',
                css('> li',
                    css(' > a',
                        Radius(spacing(0, cssv.body.radius,
                                       cssv.body.radius, 0)),
                        margin_bottom=cssv.tabs.margin),
                    margin_left='-1px'),
                padding=spacing(0, cssv.tabs.margin, cssv.tabs.margin, 0),
                float='right')),
        overflow='hidden',
        background='inherit')
