from lux.extensions.ui.lib import *     # noqa


def add_css(all):
    css = all.css
    cfg = all.app.config

    css(('[ng\:cloak], [ng-cloak], [data-ng-cloak], '
         '[x-ng-cloak], .ng-cloak, .x-ng-cloak'),
        display='none !important')

    add_scroll(all)
    add_forms(all)
    #
    if cfg['ANGULAR_VIEW_ANIMATE']:
        add_animate(all)


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
    fade.fadein = '0.3s'
    fade.fadeout = '0.3s'

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

    css('.form-error',
        css(' span', display='block'))
