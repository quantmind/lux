from ..lib import *     # noqa


def add_css(all):
    '''
    The ``navbar`` page layout should use the following template::

        <navbar></navbar>
    '''
    css = all.css
    cfg = all.app.config
    media = all.media
    vars = all.variables
    #
    # STYLING
    navbar = vars.navbar
    #
    navbar.transition.duration_in = '0.6s'
    navbar.transition.duration_out = '0.2s'
    navbar.transition.duration = '0.8s'
    navbar.collapse.max_height = px(999)
    navbar.collapse.margin.top = px(2)
    #
    # Navbar Height
    navbar.height = px(60)
    navbar.big_height = px(80)
    navbar.small_height = px(60)
    navbar.lineheight = px(20)
    navbar.offset = px(1)
    navbar.padding = 0.5*(navbar.height-navbar.lineheight)
    navbar.small_padding = 0.5*(navbar.small_height-navbar.lineheight)
    vars.animate.fade.top = navbar.height
    navbar.divider.color = '#ddd'
    #
    collapse_width = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    css('.navbar',
        css(' .navbar-nav',
            css('> li > a',
                line_height=navbar.lineheight),
            float='left',
            margin=px(0),
            height=px(navbar.small_height)),
        css(' .navbar-brand',
            css(' img', height=navbar.small_height),
            padding=0),
        margin_bottom=px(0),
        min_height=navbar.small_height)

    css('.nav-second-level li a',
        padding_left=px(37))

    css('.nav.navbar-nav > li > a',
        outline='none')

    css('.nav.main-nav > li',
        float='left')

    css('.right-divider',
        Border(left=px(1), color=navbar.divider.color),
        position='absolute',
        right=0,
        top=0,
        display='inline-block',
        height=px(navbar.height))

    css('.navbar-collapse',
        css(' .navbar-nav',
            height='auto'),
        css('.collapse',
            css(' .nav.navbar-nav > li',
                display='block'),
            css(' .navbar-right',
                padding_top=px(0)),
            css('.in',
                Transition('max-height',
                           navbar.transition.duration_in, 'ease-in'),
                border_top='1px solid #ddd',
                max_height=px(navbar.collapse.max_height)),
            Transition('max-height',
                       navbar.transition.duration_out, 'ease-out'),
            border_top='none',
            display='block',
            overflow='hidden',
            max_height=px(0)))

    large = media(min_width=collapse_width)

    large.css('.navbar',
              css(' .navbar-brand',
                  css(' img', height=navbar.height),
                  padding=spacing(0, 0, 0, 15)),
              min_height=navbar.height)

    large.css('.right-divider',
              height=px(navbar.big_height) - px(navbar.offset))

    large.css('.navbar-collapse.collapse',
              background='none')

    large.css('.navbar-collapse.collapse .navbar-right',
              padding_top=px(10))
