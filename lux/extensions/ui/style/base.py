import os

from lux.extensions.ui.lib import *

UI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def add_skins(all):
    cssv = all.variables
    classes = all.classes
    css = all.css
    #
    # Define the skins
    default = darkenskin(cssv, 'default',
                         default={'background': '#fff',
                                  'color': '#333',
                                  'border': '#ccc'},
                         hover={'background': '#F7F7F9',
                                'color': '#333',
                                'border': '#ccc'},
                         size=0)
    primary = darkenskin(cssv, 'primary', background='#0088CC', color='#fff')
    success = darkenskin(cssv, 'success', background='1DD300', color='#fff')
    error = darkenskin(cssv, 'error', background='fd0006', color='#fff')
    inverse = lightenskin(cssv, 'inverse', background='#222', color='#fff')

    return cssv.skins


def add_css(all):
    cssv = all.variables
    classes = all.classes
    css = all.css
    classes.dl_horizontal = 'dl-horizontal'
    skins = add_skins(all)
    #
    # Set defaults on body
    cssv.body.font_family = ("Helvetica,Arial,'Liberation Sans',FreeSans,"
                             "sans-serif")
    cssv.body.font_size = px(14)
    cssv.body.line_height = px(20)
    cssv.body.text_align = 'left'
    cssv.body.radius = px(5)
    cssv.body.background = '#fff'
    cssv.body.color = '#333'
    # Links
    cssv.link.font_weight = 'normal'
    #
    cssv.dl.font_weight = 'bold'
    cssv.dl.line_height = cssv.body.line_height
    #
    # Alerts
    cssv.alert.spacing = spacing(8, 14)
    cssv.alert.margin = spacing(0, 0, 5)

    cssv.label.padding = spacing(2, 4)

    cssv.code.padding = spacing(2, 4)
    #
    # Fullscreen
    cssv.fullscreen.padding = px(30)
    cssv.fullscreen.max_width = px(800)

    ##################################################### BODY AND RESETS
    css('body',
        gradient(cssv.body.background),
        CssInclude(all.get_media_url('normalize')),
        color=cssv.body.color,
        font_family=cssv.body.font_family,
        font_size=cssv.body.font_size,
        min_width=cssv.body.min_width,
        line_height=cssv.body.line_height,
        text_align=cssv.body.text_align,
        padding=0,
        margin=0)

    ##################################################### Global classes
    css('.pull-right', float='right !important')
    css('.pull-left', float='left !important')
    css('.close', float='right')
    css('.clearfix', Clearfix())
    css('markdown', display='none')
    css('.separator',
        Border(color=cssv.skins.default.default.border,
               width=spacing(1, 0, 0)),
        margin=spacing(40, 0, 39))
    css('.vpadding-small',
        padding=spacing(5, 0),
        overflow='hidden')
    css('.vpadding',
        padding=spacing(20, 0),
        overflow='hidden')

    size = lambda n: 30*n
    for n in range(1, 21):
        css('.span%s' % n, width=px(size(n)))

    # Border box by default
    css('*',
        BoxSizing('border-box'),
        css(':before,:after',
            BoxSizing('border-box')))


    ##################################################### Description
    css('dt',
        font_weight=cssv.dl.font_weight)

    css('dt, dd',
        line_height=cssv.dl.line_height)

    css('.%s' % classes.dl_horizontal,
        Clearfix(),
        css('dt',
            Textoverflow(),
            clear='left',
            float='left',
            text_align='left'))

    ##################################################### Alert
    css('.alert',
        Skin(),
        Radius(cssv.body.radius),
        css(' .close',
            position='relative',
            right='-21px',
            top='-2px'),
        text_align='left',
        margin=cssv.alert.margin,
        padding=cssv.alert.spacing)

    ##################################################### Label
    css('.label',
        Skin(),
        Radius(0.6*cssv.body.radius),
        display='inline-block',
        font_weight='bold',
        font_size=.8*cssv.body.font_size,
        padding=cssv.label.padding,
        vertical_align='baseline',
        white_space='nowrap')

    ##################################################### Fullscreen extension
    css('.fullscreen',
        Skin(only=('default', 'inverse')),
        bottom=0, left=0, right=0, top=0,
        position='fixed')

    css('.fullscreen-container',
        height=pc(100),
        margin='0 auto',
        max_width=cssv.fullscreen.max_width,
        padding=spacing(cssv.fullscreen.padding, 0))

    css('.fullscreen-sidebar',
        position='absolute',
        right=cssv.fullscreen.padding,
        top=cssv.fullscreen.padding,
        text_align='right')
