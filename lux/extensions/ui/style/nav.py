from .base import *


requires = ['base']


def add_css(all):
    cssv = all.variables
    classes = all.classes
    css = all.css

    cssv.nav.link_padding = spacing(10, 15);


    nav = css('.nav',
              Clearfix(),
              padding_left=px(0),
              margin_bottom=px(0),
              list_style='none')

    li = nav.css(' > li',
                 display='block',
                 position='relative')

    a = li.css(' > a',
               display='block',
               position='relative',
               text_decoration='none',
               padding=cssv.nav.link_padding)

    # TABS
    css('.nav-tabs',
        Skin(applyto='border'),
        Skin(' > li > a',
             gradient=False,
             active=False,
             clickable=True),
        Skin(' > li.active > a',
             gradient=False,
             default='active'),
        css(' > li',
            css(' > a',
                Border(color='transparent'),
                Radius(cssv.body.radius, 'top'),
                line_height=cssv.body.line_height,
                margin_right=px(2)),
            float='left',
            margin_bottom=px(-1)),
        border_width=spacing(0, 0, 1))

    # PILLS
    css('.nav-pills',
        css(' > li',
            css(' > a',
                Radius(cssv.body.radius))))

    # STACKED
    css('.nav-stacked',
        css(' > li',
            css(' > a',
                Radius(cssv.body.radius),
                text_align='center',
                margin_bottom=px(5)),
            float='none'),
        width=pc(100))

    # TABBABLE TABS
    css('.tab-content',
        css(' > .tab-pane',
            display='none'),
        css(' > .active',
            display='block'))


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
