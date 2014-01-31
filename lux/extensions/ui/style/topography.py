from .base import *


# Topography
def add_css(all):
    cssv = all.variables
    css = all.css
    #
    cssv.heading.font_weight = 'bold'
    cssv.heading.h1 = 2
    cssv.heading.h2 = 1.6
    cssv.heading.h3 = 1.3
    cssv.heading.h4 = 1.2
    cssv.heading.h5 = 1.1
    cssv.heading.h6 = 0.9
    cssv.paragraph.margin = spacing(0, 0, px(9))
    cssv.section.padding = spacing(0, 10)
    cssv.header.margin = spacing(10, 0)

    css('h1,h2,h3,h4,h5,h6',
        css(':first-child', margin_top=0),
        font_weight=cssv.heading.font_weight,
        text_rendering='optimizelegibility',
        margin=cssv.header.margin)
    css('h1',
        font_size=cssv.heading.h1*cssv.body.font_size,
        line_height=cssv.heading.h1*cssv.body.line_height)
    css('h2',
        font_size=cssv.heading.h2*cssv.body.font_size,
        line_height=cssv.heading.h2*cssv.body.line_height)
    css('h3',
        font_size=cssv.heading.h3*cssv.body.font_size,
        line_height=cssv.heading.h3*cssv.body.line_height)
    css('h4',
        font_size=cssv.heading.h4*cssv.body.font_size,
        line_height=cssv.heading.h4*cssv.body.line_height)
    css('h5',
        font_size=cssv.heading.h5*cssv.body.font_size,
        line_height=cssv.heading.h5*cssv.body.line_height)
    css('h6',
        font_size=cssv.heading.h6*cssv.body.font_size,
        line_height=cssv.heading.h6*cssv.body.line_height,
        text_transform='uppercase')
    css('p',
        css(':last-child', margin=0),
        margin=cssv.paragraph.margin)

    css('ul',
        css('.icons-ul',
            margin_left=px(0)))

    #################################################### SECTION
    css('.section',
        Skin(exclude='default'),
        css('h1',
            css(':first-child', margin_top=0),
            margin=spacing(30, 0, 15)),
        css('h2',
            css(':first-child', margin_top=0),
            margin=spacing(20, 0, 10)),
        css('h3,h4,h5,h6',
            css(':first-child', margin_top=0),
            margin=spacing(15, 0, 10)),
        css('ul:not(.nav) ul, ul:not(.nav) ol, ol ol, ol ul', margin_bottom=0),
        css('ul:not(.nav), ol',
            padding=0,
            margin=spacing(0, 0, px(9), px(25))),
        css('ul:not(.nav)', list_style='disc outside none'),
        css('ol', list_style='decimal outside none'),
        css('strong', font_weight='bold'),
        css('em', font_style='italic'),
        float='left',
        width=pc(100),
        margin=0,
        padding=cssv.section.padding)
