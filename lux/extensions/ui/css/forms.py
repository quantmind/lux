from ..lib import *


def add_css(all):
    css = all.css
    vars = all.variables

    css('p.form-error',
        margin=0)

    css('.form-group .help-block',
        display='none')

    css('.form-group.has-error .help-block.active',
        display='block')
