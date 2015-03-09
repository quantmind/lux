from lux.extensions.ui.lib import *


def add_css(all):
    css = all.css
    media = all.app.config['MEDIA_URL']
    vars = all.variables

    vars.background_color = '#FAFAFA'
    vars.background_footer_color = '#ededed'
    vars.background_footer_border = '#D4D4D4'
    vars.colors.blue = '#2B4E72'
    vars.navbar_height = 80
    vars.animate.fade.top = px(vars.navbar_height)

    vars.font_family = ('"freight-text-pro",Georgia,Cambria,"Times New Roman",'
                        'Times,serif')
    vars.font_size = px(18)
    vars.line_height = 1.5
    vars.color = color(0, 0, 0, 0.8)

    link = vars.link
    link.color = '#428bca'

    css('html, body, .fullpage',
        height=pc(100),
        min_height=pc(100))

    css('.angular-view',
        height=pc(100),
        min_height=pc(100))

    css('body',
        FontSmoothing(),
        letter_spacing='0.01rem',
        font_weight=400)

    css('#page-main',
        background_color=vars.background_color,
        min_height=px(200),
        padding_top=px(20),
        padding_bottom=px(50))

    css('#page-footer',
        Skin(only='default', noclass='default'),
        Border(top=px(1), color=vars.background_footer_border),
        background_color=vars.background_footer_color,
        min_height=px(200))

    css('.block',
        padding=px(10))

    css('.text-large',
        font_size=pc(150))

    page_error(all)


def page_error(all):
    css = all.css
    media = all.media
    cfg = all.app.config
    mediaurl = cfg['MEDIA_URL']
    collapse_width = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    css('#page-error',
        css(' a, a:hover',
            color=color('#fff'),
            text_decoration='underline'),
        Background(url=mediaurl+'lux/see.jpg',
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
