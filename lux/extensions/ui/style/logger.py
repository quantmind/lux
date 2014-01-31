from .base import *


def add_css(all):
    cssv = all.variables
    css = all.css

    css('.lux-logger',
        css(' pre',
            css('.debug', color='#666'),
            css('.info', color='#0066cc'),
            css('.warn', color='#cc6600'),
            css('.error', color='#ff0000'),
            css('.error', color='#ff0000'),
            border='none'),
        overflow='scroll',
        line_height=px(14),
        font_size=px(12),
        background='#ededed')
