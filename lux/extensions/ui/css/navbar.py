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
    navbar.transition.duration = '0.8s'
    navbar.padding = 0.5*(navbar.height-navbar.lineheight)
    navbar.small_padding = 0.5*(navbar.small_height-navbar.lineheight)
    vars.animate.fade.top = navbar.height
    #
    trans = navbar.transition
    collapse_width = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    css('.navbar.navbar-static-top',
        css(' .navbar-brand',
            css(' img', height=navbar.small_height),
            padding=0),
        min_height=navbar.small_height)

    css('.navbar.navbar-static-top',
        css(' .navbar-nav',
            css('> li > a',
                line_height=navbar.lineheight)))

    css('.nav-second-level li a',
        padding_left=px(37))

    css('.nav.navbar-nav > li > a',
        outline='none')

    media(min_width=collapse_width).css(
        '.navbar.navbar-static-top',
        css(' .navbar-brand',
            css(' img', height=navbar.height),
            padding=0),
        css(' .navbar-nav',
            css('> li > a',
                padding_top=navbar.padding,
                padding_bottom=navbar.padding)),
        min_height=navbar.height)

    small = media(max_width=collapse_width)

    small.css('.collapse',
              Transition('max-height', trans.duration,
                         'cubic-bezier(0, 1, 0, 1)', '0s'),
              max_height=px(0),
              visibility='hidden',
              display='block !important')

    small.css('.collapse.in',
              Transition('max-height', trans.duration,
                         'cubic-bezier(0.1, 0, 1, 0)', '0s'),
              max_height=px(999),
              visibility='visible')

    small.css('.navbar-collapse.in',
              overflow_y='hidden !important')
