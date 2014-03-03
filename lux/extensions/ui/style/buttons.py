from .base import *

from itertools import chain


input_defaults = ('text', 'password', 'date', 'datetime', 'month', 'time',
                  'week', 'number', 'email', 'url', 'search', 'tel', 'color')
input_specials = ('file', 'image', 'submit', 'reset', 'button',
                  'radio', 'checkbox')


def input_types(inputs, *extra, **kwargs):
    all = chain(extra, ('input[type="%s"]' % t for t in inputs))
    attr = kwargs.get('attr')
    if attr:
        all0 = all
        all = ('%s:%s' % (tag, attr) for tag in all0)
    return ', '.join(all)


def add_css(all):
    cssv = all.variables
    css = all.css
    #
    cssv.button.margin = px(5)
    #
    cssv.button.font_weight = 'normal'
    cssv.button.font_size = cssv.body.font_size
    cssv.button.font_family = 'inherit'
    cssv.button.disabled.opacity = 0.5
    cssv.button.disabled.cursor = 'default'
    # this is quite important as it controls all inputs paddings
    cssv.button.padding = spacing(6, 12)
    #
    cssv.button.small.font_size = 0.9*cssv.button.font_size
    cssv.button.small.padding = spacing(2, 10)
    #
    cssv.button.mini.font_size = 0.8*cssv.button.font_size
    cssv.button.mini.padding = spacing(0, 5)
    #
    cssv.button.large.font_size = 1.3*cssv.button.font_size
    cssv.button.large.padding = spacing(11, 19)
    cssv.button.large.font_weight = 'bold'
    #
    cssv.toolbar.margin = px(5)

    # Remove outline from form elements
    css('input:focus, select:focus, textarea:focus, button:focus',
        outline='none')

    css('.btn',
        #css('i',
        #    width=em(1.25),
        #    vertical_align='middle',
        #    font_size=pc(110)),
        css('.btn-mini',
            Radius(0.4*cssv.body.radius),
            font_weight='normal',
            font_size=cssv.button.mini.font_size,
            padding=cssv.button.mini.padding),
        css('.btn-small',
            Radius(0.7*cssv.body.radius),
            font_weight='normal',
            font_size=cssv.button.small.font_size,
            padding=cssv.button.small.padding),
        css('.btn-large',
            font_weight=cssv.button.large.font_weight,
            font_size=cssv.button.large.font_size,
            padding=2*cssv.button.padding),
        css('.disabled',
            Opacity(cssv.button.disabled.opacity),
            Skin(clickable='default',
                 cursor=cssv.button.disabled.cursor,
                 box_shadow='none'),
            ),
        Skin(clickable=True, prefix='btn', border_width=px(1)),
        Radius(cssv.body.radius),
        padding=cssv.button.padding,
        display='inline-block',
        text_align='center',
        vertical_align='middle',
        text_decoration='none',
        font_weight=cssv.button.font_weight,
        font_size=cssv.button.font_size,
        font_family=cssv.button.font_family,
        line_height=cssv.body.line_height)

    css('.link',
        background='none',
        border='none',
        cursor='pointer',
        padding=0)

    css('.btn-toolbar',
        margin=0,
        font_size=0)

    css('.btn-group,.btn-group-vertical',
        css(' > .btn', Radius(0)),  # Force radius to 0
        css(' > .form-control', Radius(0)),  # Force radius to 0
        css(' > .select2-container .select2-choice',
            css(' .select2-arrow', Radius(0)),
            Radius(0)),
        display='inline-block',
        position='relative',
        vertical_align='middle',
        white_space='nowrap')

    css('.btn-group',
        css(' > *',
            Radius(0),
            css(':first-child',
                border_bottom_left_radius=cssv.body.radius,
                border_top_left_radius=cssv.body.radius,
                margin_left=0),
            css(':last-child',
                border_bottom_right_radius=cssv.body.radius,
                border_top_right_radius=cssv.body.radius),
            float='left',
            position='relative'),
        css(' > * + *', margin_left='-1px'))

    css('.btn-group-vertical',
        css(' > *',
            Radius(0),
            css(':first-child',
                Radius(cssv.body.radius, 'top'),
                margin_top=0),
            css(':last-child',
                Radius(cssv.body.radius, 'bottom')),
            width=pc(100),
            min_width=pc(100),
            display='block',
            float='none',
            position='relative'),
        css(' > * + *', margin_top='-1px'))

    css('.btn-group + .btn-group',
        margin_left=px(5))

    ########################################################## TOOLBAR

    css('.toolbar',
        css('> .group',
            css('+ .group',
                margin_left=cssv.toolbar.margin),
            css('> *',
                Radius(0),
                css(':first-child',
                    Radius(cssv.body.radius, 'left'),
                    border_left_width=px(1)),
                css(':last-child',
                    Radius(cssv.body.radius, 'right')),
                border_left_width=0,
                position='relative',
                font_size=cssv.body.font_size),
            display='inline-block',
            vertical_align='middle',
            font_size=0,
            white_space='nowrap',
            position='relative'),
        margin=0)
