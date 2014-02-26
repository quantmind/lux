from .base import *

requires = ['buttons']


def add_css(all):
    cssv = all.variables
    css = all.css
    #
    cssv.input.width = px(200)
    cssv.input.height = px(34)
    cssv.input.small_width = px(90)
    cssv.form.input.margin = px(10)
    cssv.input.padding = cssv.button.padding
    cssv.form.horizontal.label_width = px(160)
    cssv.form.border.color = cssv.skins.default.default.border
    #
    # Input Shadows
    skins = ('default', 'inverse')
    cssv.input.default.shadow_color = RGBA(0, 0, 0, 0.075)
    cssv.input.default.focus_border_color = RGBA(82, 168, 236)

    cssv.input.inverse.shadow_color = '#555'
    cssv.input.inverse.focus_border_color = RGBA(82, 168, 236)
    #
    css('label',
        display='inline-block',
        margin_bottom=0.5*cssv.form.input.margin)

    css('legend',
        Border(width=spacing(0, 0, 1),
               color=cssv.form.border.color),
        display='block',
        font_size=1.5*cssv.body.font_size,
        line_height=2*cssv.body.line_height,
        margin_bottom=px(20),
        padding=0,
        width=pc(100))

    form = css('form',
               css(' .form-group',
                   Clearfix(),
                   margin_bottom=cssv.form.input.margin),
               css('.bordered',
                   Border(color=cssv.form.border.color)),
               css('.form-inline',
                   css(('select, input, .input-small, .checkbox, '
                        '.select2-container'),
                       display='inline-block',
                       margin_bottom=0,
                       vertical_align='middle'))
               )


    css('form',
        Skin(' .form-control', only=skins))

    for skin in skins:
        v = cssv.input[skin]
        focus_shadow = color(v.focus_border_color, alpha=0.6)

        css('form.%s' % skin,
            css(' .form-control',
                Shadow(0, 1, 1, color=v.shadow_color, inset=True),
                css(':focus',
                    Stack(Shadow(0, 1, 1, color=v.shadow_color, inset=True),
                          Shadow(blur=8, color=focus_shadow)),
                    border_color=v.focus_border_color)))

    css('.form-control',
        Radius(cssv.body.radius),
        Border(width=px(1), style='solid'),
        Transition('border, box-shadow', '0.2s', 'linear'),
        padding=cssv.input.padding,
        line_height=cssv.body.line_height,
        height=cssv.input.height,
        display='block',
        width=pc(100))

    # Checkbox and radio
    css('.checkbox input[type="checkbox"],.radio input[type="radio"]',
        float='left',
        margin_left=px(-20),
        margin_top=px(2))

    css('.checkbox,.radio',
        display='block',
        margin_bottom=px(10),
        margin_top=px(10),
        padding_left=px(20),
        min_height=px(20))

    css('.checkbox label,.radio label',
        cursor='pointer',
        display='inline')

    # horizontal form
    form.css('.form-horizontal',
             css(' .control-label',
                 float='left',
                 text_align='right',
                 padding_top=px(5),
                 width=cssv.form.horizontal.label_width),
             css(' .controls',
                 margin_left=cssv.form.horizontal.label_width+px(20)))


def inputs():
    ########################################################## INPUTS
    css(input_types(input_defaults, 'textarea', 'select'),
        Skin(only=('default', 'inverse')),
        Radius(cssv.body.radius),
        font_size=cssv.button.font_size,
        display='inline-block',
        vertical_align='middle',
        padding=cssv.input.padding)

    css(input_types(input_defaults),
        line_height=cssv.body.line_height,
        height=cssv.body.line_height)

    # Border transition for inputs
    css(input_types(input_defaults, 'textarea'),
        Shadow(0, 1, 1, color=RGBA(0, 0, 0, 0.075), inset=True),
        Transition('border, box-shadow', '0.2s', 'linear'))

    css(input_types(input_defaults, 'textarea', attr='focus'),
        Stack(Shadow(0, 1, 1, color=RGBA(0, 0, 0, 0.075), inset=True),
              Shadow(blur=8, color=cssv.input.focus.border_color_blur)),
        border_color=cssv.input.focus.border_color)

    css('fieldset',
        Border(width=0, style='none'),
        margin=0,
        padding=0)

    css('label',
        display='block',
        cursor='pointer',
        font_weight='normal',
        font_size=cssv.body.font_size,
        line_height=cssv.body.line_height,
        height=cssv.body.line_height)

    css(input_types(input_specials),
        width='auto')

    css('.radio, .checkbox',
        css('input[type="radio"], input[type="checkbox"]',
            float='left',
            margin_left=px(-20)),
        min_height=px(20),
        padding_left=px(20))
