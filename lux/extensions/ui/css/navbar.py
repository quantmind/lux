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
    # Navbar Height
    navbar.height = px(60)
    navbar.small_height = px(60)
    navbar.lineheight = px(20)
    navbar.padding = 0.5*(navbar.height-navbar.lineheight)
    navbar.small_padding = 0.5*(navbar.small_height-navbar.lineheight)
    vars.animate.fade.top = navbar.height
    #
    collapse_width = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    media(min_width=collapse_width).css(
        '.navbar.navbar-static-top',
        css(' .navbar-brand',
            css(' img', height=navbar.height),
            padding=0),
        css(' .navbar-nav',
            css('> li > a',
                padding_top=navbar.padding,
                padding_bottom=navbar.padding)),
        height=navbar.height)

    media(max_width=collapse_width).css(
        '.navbar.navbar-static-top',
        css(' .navbar-brand',
            css(' img', height=navbar.small_height),
            padding=0),
        height=navbar.small_height)

    css('.navbar.navbar-static-top',
        css(' .navbar-nav',
            css('> li > a',
                line_height=navbar.lineheight)))

    css('.nav-second-level li a',
        padding_left=px(37))

    css('.nav.navbar-nav > li > a',
        outline='none')
