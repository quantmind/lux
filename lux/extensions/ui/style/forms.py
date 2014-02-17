from .base import *
from .inputs import input_types, input_defaults

requires = ['inputs']


def add_css(all):
    cssv = all.variables
    css = all.css
    #
    cssv.input.width = px(200)
    cssv.input.small_width = px(90)
    cssv.form.input.margin = px(10)
    cssv.form.horizontal.label_width = px(160)
    cssv.form.border.color = cssv.skins.default.default.border.color

    #
    css('legend',
        Border(width=spacing(0, 0, 1),
               color=cssv.form.border.color),
        display='block',
        font_size=1.5*cssv.body.font_size,
        line_height=2*cssv.body.line_height,
        margin_bottom=px(20),
        padding=0,
        width=pc(100))

    css('input, textarea',
        width=cssv.input.width)

    css('.input-small',
        width=cssv.input.small_width),

    form = css('form',
               css('.bordered',
                   Border(color=cssv.form.border.color)),
               css('.inline',
                   css(('select, input, .input-small, .checkbox, '
                        '.select2-container'),
                       display='inline-block',
                       margin_bottom=0,
                       vertical_align='middle')),
               css(input_types(input_defaults, 'textarea', 'select',
                               '.checkbox', '.select2-container'),
                   display='block',
                   margin_bottom=cssv.form.input.margin),
               css('label',
                   margin_bottom=0.5*cssv.form.input.margin)
               )

    # horizontal form
    form.css('.horizontal',
             css(' .control-group',
                 Clearfix()),
             css(' .control-label',
                 float='left',
                 text_align='right',
                 padding_top=px(5),
                 width=cssv.form.horizontal.label_width),
             css(' .controls',
                 margin_left=cssv.form.horizontal.label_width+px(20)))
