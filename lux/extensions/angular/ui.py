from lux.extensions.ui.lib import *


def add_css(all):
    css = all.css
    cfg = all.app.config

    css(('[ng\:cloak], [ng-cloak], [data-ng-cloak], '
         '[x-ng-cloak], .ng-cloak, .x-ng-cloak'),
        display='none !important')

    add_navbar(all)
    add_scroll(all)
    #
    if cfg['ANGULAR_VIEW_ANIMATE']:
        add_animate(all)


def add_navbar(all):
    '''
    The navbar2 page layout should use the following template

    <div class="navbar2-wrapper navbar-{{navbar.theme}}" ng-controller="Navigation">
        <navbar2></navbar2>
        <div class='navbar2-page'>
            <div class='row'>
                ...
            </div>
            <div class='row'>
                ...
            </div>
        </div>
    </div>
    '''
    css = all.css
    cfg = all.app.config
    media = all.media
    vars = all.variables
    #
    # NAVBAR (TOP)
    navbar = vars.navbar
    navbar.height = px(50)
    #
    # SIDEBAR
    sidebar = vars.sidebar
    sidebar.default.border = '#E7E7E7'
    sidebar.width = px(250)
    min_width_collapse = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    # wraps the navbar2 and the main page
    css('.navbar2-wrapper',
        width=pc(100),
        min_height=pc(100))

    css('.navbar2-page',
        background=vars.background,
        padding=spacing(navbar.height+20, 15, 0))

    media(min_width=min_width_collapse).css(
        '.navbar2-page',
        margin=spacing(0, 0, 0, sidebar.width)).css(
        '.navbar2-wrapper.navbar-default .navbar2-page',
        Border(color=sidebar.default.border, left=px(1)))

    media(min_width=min_width_collapse).css('.sidebar',
        margin_top=navbar.height+1,
        position='absolute',
        width=sidebar.width,
        z_index=1)


def add_scroll(all):
    css = all.css
    vars = all.variables
    vars.scroll.background = 'inherit'

    css('.scroll-target',
        css('.finished',
            Transition('all', '2s', 'ease'),
            background='inherit'),
        background=vars.scroll.background)


def add_animate(all):
    css = all.css
    vars = all.variables

    css('body',
        CssInclude('animate'))

    css('.animate-fade',
        css('.ng-enter,.ng-leave',
            position='absolute',
            left=0,
            right=0),
        css('.ng-enter',
            Animation('fadeIn', '1s')),
        css('.ng-leave',
            Animation('fadeOut', '1s')))