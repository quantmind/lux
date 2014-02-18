import os

from lux.extensions.ui.lib import *

UI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skins(all):
    darkenskin('default', '#333', '#e5e5e5',
               description='default skin',
               lighten=5)
    darkenskin('primary', '#fff', '#0088CC',
               description='Extra visual weight',
               lighten=15)
    darkenskin('error', '#fff', '#DA4F49',
               description=('Indicates a dangerous or potentially'
                            ' negative action'))
    darkenskin('success', '#fff', '#51A351',
               description='Indicates a success')


def add_css(all):
    cssv = all.variables
    classes = all.classes
    css = all.css
    classes.dl_horizontal = 'dl-horizontal'
    #
    # Define the skins
    base = createskin(cssv, 'base',
                      default={'background': '#fff',
                               'color': '#333',
                               'border': {'color': '#e5e5e5'}},
                      class_name=None)
    default = darkenskin(cssv, 'default', base.default, class_name=None)
    primary = darkenskin(cssv, 'primary', base.default,
                         background='#0088CC', color='#fff')
    success = darkenskin(cssv, 'success', base.default,
                         background='1DD300', color='#fff')
    error = darkenskin(cssv, 'error', base.default,
                       background='fd0006', color='#fff')
    inverse = lightenskin(cssv, 'inverse', base.default,
                          background='#222', color='#fff')
    createskin(cssv, 'zen',
               default={'background': '#fff',
                        'color': '#999',
                        'border': 'none'},
               hover={'color': '#333'},
               active={'color': '#333'})
    createskin(cssv, 'zendark',
               default={'background': '#1D1F21',
                        'color': '#A4B1B1',
                        'border': 'none'},
               hover={'color': '#DBE0E0'},
               active={'color': '#DBE0E0'})
    #
    #color = '#08c'
    #simpleskin(cssv, 'link', color=color, text_decoration='none',
    #           hover_color=darken(color, 15),
    #           hover_text_decoration='underline', class_name=None)
    #
    # Set defaults on body
    cssv.body.font_family = ("Helvetica,Arial,'Liberation Sans',FreeSans,"
                             "sans-serif")
    cssv.body.font_size = px(14)
    cssv.body.line_height = px(20)
    cssv.body.text_align = 'left'
    cssv.body.radius = px(5)
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
    if all.config('ICON_PROVIDER') == 'fontawesome':
        css('body',
            CssInclude(os.path.join(UI_DIR, 'media', 'font-awesome.css'),
                       location='ui', replace='../font'))

    css('body',
        gradient(base.default.background),
        CssInclude(all.get_media_url('normalize')),
        color=base.default.color,
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
        Border(cssv.skins.default.default.border.color,
               width=spacing(1, 0, 0)),
        margin=spacing(40, 0, 39))
    css('.vpadding-small',
        padding=spacing(5, 0),
        overflow='hidden')
    css('.vpadding',
        padding=spacing(20, 0),
        overflow='hidden')
    css('.fullscreen',
        bottom=0, left=0, right=0, top=0,
        position='fixed')

    size = lambda n: 30*n
    for n in range(1, 21):
        css('.span%s' % n, width=px(size(n)))

    # Border box by default
    css('*',
        BoxSizing('border-box'),
        css(':before,:after',
            BoxSizing('border-box')))

    ##################################################### Anchor
    #css('a',
    #    Skin(only='link', clickable=True),
    #    font_weight=cssv.link.font_weight
    #)

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
