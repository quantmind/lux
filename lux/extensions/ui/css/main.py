from ..lib import *     # noqa


def add_css(all):
    css = all.css
    vars = all.variables

    vars.line_height = 1.42857
    vars.color = color('#333')
    vars.background = color('#fff')
    # Helper classes
    vars.push_bottom = '20px !important'

    black = color('#000')
    vars.colors.gray_darker = lighten(black, 13.5)
    vars.colors.gray_dark = lighten(black, 20)
    vars.colors.gray = lighten(black, 50)
    vars.colors.gray_light = lighten(black, 70)
    vars.colors.gray_lighter = lighten(black, 93.5)

    # SKINS
    skins = vars.skins
    default = skins.default
    default.background = color('#f7f7f9')

    inverse = skins.inverse
    inverse.background = color('#3d3d3d')

    css('body',
        font_family=vars.font.family,
        font_size=vars.font.size,
        line_height=vars.line_height,
        font_style=vars.font.style,
        background=vars.background,
        color=vars.color)

    classes(all)
    anchor(all)


def classes(all):
    css = all.css
    vars = all.variables

    css('.fullpage',
        height=pc(100),
        min_height=pc(100))

    css('.push-bottom',
        margin_bottom=vars.push_bottom)

    css('.lazyContainer',
        css(' > .content',
            top=0,
            left=0,
            position='absolute',
            width=pc(100),
            min_height=pc(100)),
        position='relative')


def anchor(all):
    '''Both ``anchor.color`` and ``anchor.color_hover`` variables are
    left unspecified so that this rule only apply when an set their
    values
    '''
    css = all.css
    vars = all.variables

    vars.anchor.color = None
    vars.anchor.color_hover = None

    css('a',
        css(':hover',
            color=vars.anchor.color_hover),
        color=vars.anchor.color)
