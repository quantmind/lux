from .base import *


requires = ['base']


def body_background(gradient):
    end = gradient.end
    return lighten(end, 5)


def add_css(all):
    cssv = all.variables
    css = all.css
    #
    cssv.datatable.head.font_weight = 'bold'
    cssv.datagrid.radius = cssv.body.radius
    cssv.datatable.padding = spacing(4, 6)
    cssv.pagination.padding = spacing(4, 12)

    dg = css('.datagrid',
             InlineBlock(),
             css(' > table',
                 Radius(cssv.datagrid.radius),
                 css(' th, td',
                     padding=cssv.datatable.padding),
                 css(' > thead',
                     css(' > tr',
                         border='none'),
                     css(' > tr:first-child',
                         Radius(cssv.datagrid.radius, 'top'),
                         css(' > th:first-child',
                             Radius(cssv.datagrid.radius, 'top-left')),
                         css(' > th:last-child',
                             Radius(cssv.datagrid.radius, 'top-right'))),
                     border='none'),
                 border_collapse='separate',
                 border_spacing=0))

    dg.css('th.sortable',
           cursor='pointer',
           vertical_align='bottom')
    dg.css(' a.sortable-toggle',
           float='right',
           margin_left=px(3))

    if False:
        dg.css(
                   css('th',
                       css('.sortable',
                            cursor='pointer'),
                        vertical_align='bottom'),
                    css('.stripped',
                        Skin('tbody tr:nth-child(2n+1) td',
                             applyto=('background', 'color'),
                             transform=lighten)),
                    #
                    css(' .hd',
                        font_weight=cssv.datatable.head.font_weight),
                    #
                    css('.footer tbody tr:last-child',
                        css(' td:last-child',
                            border_bottom_right_radius=0),
                        css(' td:first-child',
                            border_bottom_left_radius=0)),
                    #
                    # Sortable
                    css(' a.sortable-toggle',
                        padding=spacing(2, 0, 2, 10)),
                    #
                    text_align='left')

    # TABLE LAYOUT
    dg.css('.table',
            Skin(' td', applyto=['border']),
            css(' td', border_width=spacing(1, 0, 0)))

    # GRID LAYOUT
    dg.css('.grid',
           Skin(' table', applyto=['border']),
           #
           # header grid
           Skin(' tr.row > th',  border_width=spacing(0, 0, 1, 1)),
           css(' tr.row > th:first-child', border_left='none'),
           #
           # Body grid
           Skin(' tr.row > td', applyto=['border'],
                border_width=spacing(0, 0, 1, 1)),
           css(' tr.row > td:first-child', border_left='none'),
           css(' tbody > tr.row:last-child > td',
                border_bottom='none'))

    css('.section',
        css(' .datatable',
            margin=spacing(15, 0, 15)))

    ########################################################## PAGINATION
    css('.pagination',
        Skin('ul > li > a',
             clickable=True, gradient=False,
             border_width=spacing(1, 1, 1, 0)),
        css('ul',
            css('> li',
                css('> a',
                    padding=cssv.pagination.padding,
                    float='left'),
                css(':first-child > a',
                    Radius(spacing(cssv.body.radius, 0, 0, cssv.body.radius)),
                    border_left_width=px(1)),
                css(':last-child > a',
                    Radius(spacing(0, cssv.body.radius, cssv.body.radius, 0))),
                display='inline'),
            Radius(cssv.body.radius),
            display='inline-block',
            margin=0),
        css('.mini',
            css('ul > li > a',
                padding=0.3*cssv.pagination.padding,
                font_size=cssv.button.mini.font_size)),
        css('.small',
            css('ul > li > a',
                padding=0.5*cssv.pagination.padding,
                font_size=cssv.button.small.font_size)),
        css('.large',
            css('ul > li > a',
                padding=2*cssv.pagination.padding,
                font_size=cssv.button.large.font_size))
        )

    ########################################################## RESPONSIVE TABLE
    all.add(Media('only screen and (max-width: 767px)')
            .css('.datagrid',
                 css('table, thead, tbody, tfoot, th, td, tr',
                     display='block'),
                 css('thead tr, tfoot tr',
                     position='absolute',
                     top='-9999px',
                     left='-9999px'),
                 css('td',
                     css(':before',
                         Opacity(0.8),
                         content='attr(data-content)',
                         position='absolute',
                         width=pc(45),
                         left=px(6),
                         whitespace='nowrap'),
                     position='relative',
                     padding_left=pc(50)),
                 css('tr:first-child',
                     css('td:first-child',
                         border_top_left_radius=cssv.body.radius,
                         border_top_right_radius=cssv.body.radius)),
                 css('tr:last-child',
                     css('td:first-child',
                         border_bottom_left_radius=0),
                     css('td:last-child',
                         border_bottom_left_radius=cssv.body.radius)),
                 css('.table, .grid',
                     Skin(applyto=['border'], border_width=spacing(0, 0, 1)),
                     Skin('td', applyto=['border'],
                          border_width=spacing(1, 1, 0))),
                 Skin('tr:nth-of-type(2n+1)', applyto=['background', 'color'],
                      gradient=body_background),
                 width=pc(100)))
