from lux.extensions.ui import *     # noqa


def add_css(all):
    css = all.css
    vars = all.variables
    text = vars.text_content

    text.standard_width = px(790)
    text.fullwidth.padding = px(20)

    css('.text-content',
        css(' > .standard',
            margin_right='auto',
            margin_left='auto',
            max_width=text.standard_width))
