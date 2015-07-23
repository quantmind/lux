from ..lib import *     # noqa


def add_css(all):
    css = all.css
    vars = all.variables

    vars.modal_height = px(350)

    css('.cannot-undo',
        font_weight=600)

    css('.modal-info',
        font_weight=600)

    css('.modal-items',
        max_height=px(vars.modal_height),
        overflow_y='auto')
