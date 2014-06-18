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
    cssv.input.default.inset_shadow = RGBA(0, 0, 0, 0.075)
    cssv.input.default.focus_border = RGBA(82, 168, 236)
    cssv.input.inverse.inset_shadow = '#555'
    #
    css('fieldset',
        Border('none', width=0),
        margin=0,
        padding=0)

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
                   #Clearfix(),
                   margin_bottom=cssv.form.input.margin),
               css('.form-inline',
                   css(('select, input, .input-small, .checkbox, '
                        '.select2-container'),
                       display='inline-block',
                       margin_bottom=0,
                       vertical_align='middle'))
               )

    fc = css('.form-control',
             Radius(cssv.body.radius),
             Border(width=px(1)),
             Transition('border, box-shadow', '0.2s', 'linear'),
             padding=cssv.input.padding,
             line_height=cssv.body.line_height,
             height=cssv.input.height,
             display='block',
             width=pc(100))

    css('textarea.form-control,select[multiple],select[size]',
        height='auto')

    # Checkbox and radio
    css('.checkbox input[type="checkbox"],.radio input[type="radio"]',
        float='left',
        margin_left=px(-20),
        margin_top=px(2))

    css('.checkbox,.radio',
        display='block',
        margin_bottom=cssv.form.input.margin,
        padding_left=px(20),
        min_height=px(20))

    css('.checkbox label,.radio label',
        cursor='pointer',
        display='inline')

    # Textarea
    css('.textarea',
        display='block',
        margin_bottom=cssv.form.input.margin)

    # horizontal form
    form.css('.form-horizontal',
             css(' .control-label',
                 float='left',
                 text_align='right',
                 padding_top=px(5),
                 width=cssv.form.horizontal.label_width),
             css(' .controls',
                 margin_left=cssv.form.horizontal.label_width+px(20)))

    # Inline forms
    form.css('.form-inline',
             css(' .form-group',
                 display='inline-block',
                 margin_bottom=0,
                 vertical_align='middle'),
             css(' .checkbox, .radio',
                 display='inline-block',
                 margin_bottom=0,
                 margin_top=0,
                 padding_left=0,
                vertical_align='middle'),
             css(' .checkbox input[type="checkbox"],'
                 ' .radio input[type="radio"]',
                 float='none',
                 margin_left=0,
                 margin_top=0))

    # Select styling
    css('body',
        CssInclude(all.get_media_url('select'), location='ui/'))

    css('.form-control.select2-container',
        css(' .select2-choice',
            css(' > .select2-chosen',
                height=cssv.input.height,
                line_height=cssv.input.height),
            height=cssv.input.height,
            line_height=cssv.input.height),
        padding=0,
        border='none',
        height='auto',
        width=pc(100))

    # Styling
    for skin in cssv.skins:
        if not skin.is_skin:
            continue
        name = skin.name
        skin = skin.default
        border = skin.border
        selector = '.form-control'
        if name != 'default':
            selector = '.%s .form-control' % name
        input = cssv.input[name]
        focus_border = None
        if input:
            inset_shadow = input.inset_shadow
            focus_border = input.focus_border
            css(selector,
                Shadow(0, 1, 1, color=inset_shadow, inset=True),
                background='inherit',
                color=skin.color)
        else:
            inset_shadow = cssv.input.default.inset_shadow
        #
        if not focus_border:
            focus_border = border
        focus_shadow = color(focus_border, alpha=0.6)
        #
        css(selector,
            Border(width=px(1), color=border),
            css(':focus',
                Stack(Shadow(0, 1, 1, color=inset_shadow, inset=True),
                      Shadow(blur=8, color=focus_shadow)),
                border_color=focus_border))




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

    # Select styling

    css('body',
        CssInclude(all.get_media_url('select'), location='ui/'))

    def select_height():
        p = as_value(cssv.input.padding)
        l = as_value(cssv.body.line_height)
        return l + p.top + p.bottom + px(2)

    def select_width():
        p = as_value(cssv.input.padding)
        l = as_value(cssv.input.width)
        return l + p.left + p.right + px(2)

    css('select',
        line_height=Lazy(select_height),
        height=cssv.input.height,
        width=Lazy(select_width))

    css('select[multiple], select[size]',
        height='auto')

    css('div.colored',
        Skin(),
        min_height=px(20),
        padding_left=px(5))
