from lux.extensions.ui.lib import *


def add_css(all):
    css = all.css
    cfg = all.app.config

    css(('[ng\:cloak], [ng-cloak], [data-ng-cloak], '
         '[x-ng-cloak], .ng-cloak, .x-ng-cloak'),
        display='none !important')

    add_navbar(all)
    add_scroll(all)
    add_forms(all)
    #
    if cfg['ANGULAR_VIEW_ANIMATE']:
        add_animate(all)


def add_navbar(all):
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
    navbar.default.background = '#f8f8f8'
    #
    # NAVBAR (TOP)
    navbar.height = px(50)
    #
    # SIDEBAR
    sidebar = vars.sidebar
    sidebar.default.border = '#E7E7E7'
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

    fade = vars.animate.fade
    fade.top = 0
    fade.left = 0
    fade.fadein ='0.3s'
    fade.fadeout ='0.3s'

    # Animate fade-in fade-out
    css('.animate-fade',
        css('.ng-enter,.ng-leave',
            position='absolute',
            width=pc(100),
            top=fade.top,
            left=fade.left),
        css('.ng-enter',
            Transition('all', fade.fadein, 'linear'),
            css('.ng-enter-active',
                Opacity(1)),
            Opacity(0)),
        css('.ng-leave',
            Transition('all', fade.fadeout, 'linear'),
            css('.ng-leave-active',
                Opacity(0)),
            Opacity(1)))

    c = vars.animate.amcollapse
    c.duration = '0s'
    # Animate for navbar collapse
    css('.collapse.am-collapse',
        Animation(duration=c.duration, function='ease', fill_mode='backwards'),
        css('.in-remove',
            Animation('collapse'),
            display='block'),
        css('.in-add',
            Animation('expand')))


def add_forms(all):
    css = all.css
    vars = all.variables

    css('.form-error',
        css(' span', display='block'))

