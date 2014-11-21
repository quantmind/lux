from lux.extensions.ui import *


def add_css(all):
    '''Css rules for blogapp'''
    css = all.css
    vars = all.variables
    media = all.media
    cfg = all.app.config
    mediaurl = cfg['MEDIA_URL']
    collapse_width = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    vars.color = color('#555')
    # Override default background color
    vars.colors.default_background = color('#efeae2')
    # set anchor colors
    vars.anchor.color = color('#000')
    vars.anchor.color_hover = color('#000')
    vars.font_family = ('"freight-text-pro",Georgia,Cambria,"Times New Roman",'
                        'Times,serif')
    vars.font_size = px(18)
    vars.font.size_jumbo = px(40)
    vars.line_height = 1.5
    vars.skins.default.background = vars.colors.default_background
    vars.scroll.background = '#99EBFF'
    vars.animate.fade.top = px(20)

    # Navbar specific css
    navbar(all)
    # Blog zen form
    zenform(all)
    # Blog css
    blog(all)

    css('html, body, .fullpage',
        min_height=pc(100),
        height=pc(100))

    css('.fullpage',
        Clearfix(),
        padding=0,
        margin=0)

    # Small page template
    media(min_width=collapse_width).css(
        '.small-page',
        Radius(px(5)),
        CenterBlock(),
        Shadow(0, 0, px(8), px(1), color=color(0, 0, 0, 0.8)),
        background=color(255, 255, 255),
        margin_top=px(40),
        max_width=px(500))

    css('#page-content',
        min_height=px(400),
        padding=spacing(20, 0),
        background_color='#fff')

    css('#page-footer',
        padding=spacing(20, 0),
        background_color=vars.colors.default_background,
        min_height=px(300))

    # ERROR PAGE
    css('#page-error',
        css(' a, a:hover',
            color=color('#fff'),
            text_decoration='underline'),
        Background(url=mediaurl+'blogapp/see.jpg',
                   size='cover',
                   repeat='no-repeat',
                   position='left top'),
        color=color('#fff'))
    css('.error-message-container',
        BoxSizing('border-box'),
        padding=spacing(40, 120),
        background=color(0, 0, 0, 0.4),
        height=pc(100)),
    css('.error-message',
        css(' p',
            font_size=px(50)))
    media(max_width=collapse_width).css(
        '.error-message p',
        font_size=px(32)).css(
        '.error-message-container',
        text_align='center',
        padding=spacing(40, 0))

    # WIDTH classes
    for i in range(1, 10):
        size = i*100
        css('.maxwidth%d' % size,
            max_width=px(size))

    css('input.borderless',
        outline='none',
        border=0)

    css('.text-jumbo',
        font_size=vars.font.size_jumbo)

    css('.searchBox',
        margin_bottom=px(30))

    # Single column layout
    css('.single-column',
        CenterBlock(),
        max_width=px(900))


def navbar(all):
    css = all.css
    vars = all.variables

    media_url = all.app.config['MEDIA_URL']
    navbar = vars.navbar
    navbar.height = px(100)
    vars.animate.fade.top = navbar.height+1
    vars.navbar.default.background = vars.colors.default_background

    css('nav#home',
        css(' .navbar-brand',
            css(' img', height=navbar.height),
            min_height=navbar.height,
            padding=0),
        css(' .nav.navbar-nav',
            margin_top=px((navbar.height - 50)/2)),
        margin_bottom=0)


def zenform(all):
    css = all.css
    vars = all.variables

    css('.blogStatus',
        padding=spacing(5, 15))

    css('.zen form',
        css(' .form-control',
            box_shadow='none',
            border='none',
            color=color('#000'),
            font_size=px(20)),
        css(' textarea',
            resize='none'),
        css(' input[name=title]',
            font_size=vars.font.size_jumbo,
            height=px(60)),
        css(' textarea[name=description]',
            font_size=px(20),
            color=('#555')),
        css(' textarea[name=body]',
            font_size=px(16),
            color=('#444')))


def blog(all):
    css = all.css
    vars = all.variables
    vars.list_image_width = 140
    vars.list_image_xs_height = 150

    css('.media-list > .media',
        css(' > a',
            css(' .post-body',
                margin_left=px(vars.list_image_width+20)),
            css(' h3',
                font_weight='normal',
                color=vars.colors.gray_dark),
            text_decoration='none',
            color=vars.colors.gray))

    css('.post-image',
        width=px(vars.list_image_width),
        max_height=px(vars.list_image_width),
        float='left',
        height='auto')

    css('.post-image-xs',
        max_height=px(vars.list_image_xs_height),
        max_width=pc(90),
        width='auto')

    css('.blogActions',
        css(' a',
            min_width=px(80),
            margin=spacing(5, 0)))

    css('.modal-backdrop',
        background=color(255, 255, 255, 0.95))

    css('.modal-dialog',
        text_align='center',
        outline='none',
        overflow='hidden',
        max_width=px(580),
        padding=spacing(100, 80),
        background=color('#fff'))

    css('.modal-footer',
        text_align='center',
        border='none')
