from lux.extensions.ui import *


def add_css(all):
    css = all.css

    css('.dir-entry-image',
        css(' img',
            width=px(120),
            height='auto'),
        overflow='hidden',
        max_height=px(90))
