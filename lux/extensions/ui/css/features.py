from ..lib import *     # noqa


def add_css(all):
    css = all.css
    media = all.media

    css('.features article',
        Clearfix(),
        float='left',
        padding=px(30),
        width=pc(33.33))

    media(max_width=px(978)).css(
        '.features article',
        width=pc(50))

    media(max_width=px(600)).css(
        '.features article',
        width='auto',
        float='none')
