from ..lib import *     # noqa


def add_css(all):
    '''
    The navbar2 page layout should use the following template::

        <navbar2>
            ...
        </navbar2>
    '''
    css = all.css
    cfg = all.app.config
    media = all.media
    vars = all.variables
    #
    # STYLING
    navbar = vars.navbar
    #
    # NAVBAR (TOP)
    navbar.height = px(50)
    #
    # SIDEBAR
    sidebar = vars.sidebar
    sidebar.width = px(250)
    min_width_collapse = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    css('.navbar',
        css(' .navbar-toggle',
            margin_top=0.5*(navbar.height-50)+8),
        min_height=navbar.height)

    css('.navbar-default',
        background=navbar.default.background)

    # wraps the navbar2 and the main page
    css('.navbar2-wrapper',
        css(' > .navbar', margin_bottom=0),
        width=pc(100),
        min_height=pc(100))

    css('.navbar2-page',
        background=vars.background,
        padding=spacing(15, 15, 0))

    media(min_width=min_width_collapse).css(
        '.navbar2-page',
        margin=spacing(0, 0, 0, sidebar.width)).css(
        '.navbar2-wrapper.navbar-default .navbar2-page',
        Border(color=sidebar.default.border, left=px(1)))

    media(min_width=min_width_collapse).css(
        '.sidebar',
        margin_top=navbar.height+1,
        position='absolute',
        width=sidebar.width,
        z_index=1)

    css('.nav-second-level li a',
        padding_left=px(37))

    css('.nav.navbar-nav > li > a',
        outline='none')
