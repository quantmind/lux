from lux.extensions.ui.lib import *


################################################# FLUID GRID
class Gridfluid(Mixin):
    grid_class = '-fluid'
    unit = '%'

    def __init__(self, columns, gutter=2.5641):
        self.gutter = gutter
        self.columns = columns

    def __call__(self, elem):
        columns = as_value(self.columns)
        if columns <= 1:
            raise ValueError('Grid must have at least 2 columns')
        gutter = as_value(self.gutter)
        if gutter < 0:
            raise ValueError('gutter must be positive')
        span = (100 - (columns-1)*gutter)/columns
        if span <= 0:
            raise ValueError('gutter too large')
        row = elem.css('.grid%s' % columns,
                       Clearfix(),
                       width=pc(100))
        for s in range(1, columns+1):
            w = round(s*span + (s-1)*gutter, 4)
            row.css('> .span%s' % s, width=pc(w))
        row.css('> [class*="span"]',
                float='left',
                margin_left='{0}{1}'.format(self.gutter, self.unit))
        row.css('> [class*="span"]:first-child', margin_left=0)


def add_css(all):
    css = all.css
    cssv = all.variables
    cssv.grid.fluid_padding = px(20)
    cssv.grid.fixed_width = px(940)
    cssv.centerpage.width = px(400)
    cssv.centerpage.margin = px(60)
    add_content_css(all)

    background = darken(as_value(cssv.skins.default.default.background).end,
                        10)

    css('.cms-page',
        Skin(applyto=['background', 'color']),
        width='100%')

    css('.grid',
        Clearfix(),
        css('.fluid',
            padding_left=cssv.grid.fluid_padding,
            padding_right=cssv.grid.fluid_padding),
        css('.fixed',
            width=cssv.grid.fixed_width,
            margin='auto'),
        css(':first-child',
            margin_top=0),
        margin_top=cssv.grid.fluid_padding)

    css(' .column',
        css(' .row',
            css(':first-child',
                margin_top=0),
            margin_top=cssv.grid.fluid_padding))
    #
    css('.cms-block, .cms-content',
        overflow='hidden')
    #
    css('.cms-grid',
        Opacity(0))
    css('.cms-control',
        Skin(' > .body'),
        display='none')
    # Position toolbar
    css('.cms-content-toolbar',
        padding=spacing(5, 0),
        font_size=0.8*cssv.body.font_size,
        overflow='hidden')
    #
    css('.editing',
        css(' .cms-grid',
            css(' .row-control',
                margin_top=cssv.grid.fluid_padding),
            css(' .cms-column',
                css('.active', background=background),
                Skin(only='default', applyto=['background'], gradient=False),
                min_height=px(20))))
    #
    css('.block-control',
        css(':last-child',
            margin_bottom=0),
        margin_bottom=cssv.grid.fluid_padding),
    #
    # Center Page
    css('.center-page',
        width=cssv.centerpage.width,
        margin=spacing(cssv.centerpage.margin, 'auto'))

    css('.cms-info',
        display='inline-block',
        position='relative',
        vertical_align='middle',
        line_height=px(30),
        padding=spacing(0,10))

    Gridfluid(24)(all)


def add_content_css(all):
    css = all.css
    cssv = all.variables
    imargin = cssv.form.input.margin

    def margin_right():
        imargin = cssv.form.input.margin.value()
        return px(1) - (imargin.left + imargin.right + px(3))

    css('form.content-form',
        css(' .control-group',
            display='inline'),
        css('fieldset',
            css('input, textarea',
                BoxSizing('border-box'),
                min_width=pc(100),
                max_width=pc(100),
                display='block'),
            css('input',
                min_height=px(35)),
            css('textarea',
                resize='vertical',
                min_height=px(200),
                max_height=px(500)),
            position='relative',
            padding=px(10)))
