from .base import *


def add_css(all):
    cssv = all.variables
    css = all.css

    css('.columns',
        css(' .column',
            display='block'))
