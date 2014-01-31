from .base import *


def add_css(all):
    cssv = all.variables
    css = all.css
    #
    cssv.code.padding = px(9)
    cssv.code.line_height = cssv.body.line_height
    cssv.code.font_size = cssv.body.font_size - px(1)
    cssv.code.radius = cssv.body.radius
    #
    skins = cssv.code.skins
    default = skins.default
    #
    default.color = cssv.skins.default.default.color
    default.background = '#F7F7F9'
    default.border = '#E1E1E8'
    default.linenum = lighten(default.color, 30)
    default.com = '#93a1a1'
    default.lit = '#195f91'
    default.pun = '#93a1a1'
    default.opn = default.pun
    default.clo = default.pun
    default.fun = '#dc322f'
    default.str = '#D14'
    default.atv = default.str
    default.kwd = '#005580'
    default.tag = '#1E347B'
    default.typ = 'teal'
    default.atn = default.typ
    default.dec = default.typ
    default.var = 'teal'
    default.pln = '#48484c'

    ##################################################### Code

    css('pre',
        Radius(cssv.code.radius),
        padding=cssv.code.padding,
        line_height=cssv.code.line_height,
        font_size=cssv.code.font_size,
        white_space='pre-wrap',
        word_break='break-all',
        word_wrap='break-word')

    pretty = css(
        '.prettyprint',
        css('.linenums',
            Stack(Shadow(40, color='#fbfbfc', inset=True),
                  Shadow(41, color='#ececf0', inset=True))),
        css(' .com', color=cssv.skins.code.com),
        css(' .lit', color=default.lit),
        css(' .pun', color=default.pun),
        css(' .opn', color=default.opn),
        css(' .clo', color=default.clo),
        css(' .fun', color=default.fun),
        css(' .str', color=default.str),
        css(' .atv', color=default.atv),
        css(' .kwd', color=default.kwd),
        css(' .tag', color=default.tag),
        css(' .typ', color=default.typ),
        css(' .atn', color=default.atn),
        css(' .dec', color=default.dec),
        css(' .var', color=default.var),
        css(' .pln', color=default.pln),
        Skin(only='default', gradient=lambda g: g.middle),
        color=default.color)

    #Specify class=linenums on a pre to get line numbering
    pretty.css('ol',
               css('.linenums',
                   css('li',
                       padding_left=px(12),
                       color=default.linenum,
                       line_height=cssv.code.line_height,
                       text_shadow='0 1px 0 #fff'),
                   margin=spacing(0, 0, 0, 33)),
               padding=0)
