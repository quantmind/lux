from ..lib import *     # noqa


def add_css(all):
    css = all.css
    vars = all.variables

    css('p.form-error',
        margin=0)

    css('.form-group',
        css(' .help-block',
            display='none'),
        css(' .error-block',
            font_size=vars.font.size_small))

    css('.form-group.has-error .help-block.active',
        display='block')
