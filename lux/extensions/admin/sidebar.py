from lux.extensions.ui.lib import *     # noqa


def add_css(all):
    '''Css rules for sidebar
    '''
    css = all.css
    media = all.media
    vars = all.variables
    cfg = all.app.config

    # Sidebar variables container
    navbar = vars.navbar
    sidebar = vars.sidebar
    sidebar.width = px(250)
    sidebar.transition.easing = 'cubic-bezier(0.2, 0.3, 0.25, 0.9)'
    sidebar.transition.duration = '0.2s'
    sidebar.overlay.color = color(0, 0, 0, 0.1)
    sidebar.toggle.margin = px(15)
    sidebar.toggle.size = px(21)
    sidebar.toggle.size_small = px(19)
    sidebar.toggle.padding = spacing(28, 22)
    # Style
    sidebar.background = '#2D3C4B'
    sidebar.color = '#eee'
    sidebar.toggle.border = '1px solid #ddd'
    sidebar.info.p.color = '#ccc'
    sidebar.info.background = '#425466'
    sidebar.link.color = '#fff'
    sidebar.link.background = '#263647'
    #
    sidebar.menu.max_height = px(999)

    trans = sidebar.transition
    # Why this? because unitary operations don't work yet and px(0) fails
    sidebar.width_neg = px(1) - sidebar.width - px(1)
    collapse_width = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    media(min_width=collapse_width).css(
        '.navbar',
        css(' a.sidebar-toggle',
            font_size=sidebar.toggle.size,
            padding=sidebar.toggle.padding))

    css('.fullwidth',
        width=pc(100),
        overflow_x='hidden')

    css('.sidebar-body',
        position='relative')

    css('.content-wrapper',
        position='relative',
        top=px(navbar.height),
        bottom=0,
        left=0,
        right=0)

    css('.sidebar-page, .sidebar-navbar > nav',
        Transform(0, 0),
        Transition('all', trans.duration, trans.easing))

    css('.overlay',
        position='absolute',
        background_color=sidebar.overlay.color,
        display='none',
        width='100%',
        bottom=0,
        left=0,
        top=0,
        z_index=800)

    css('.sidebar',
        Transition('all', trans.duration, trans.easing),
        css('.sidebar-left',
            Transform(sidebar.width_neg, 0),
            left=0),
        css('.sidebar-right',
            Transform(0, sidebar.width_neg),
            right=0),
        css(' a',
            css(':hover',
                text_decoration='none'),
            outline='none',
            text_decoration='none',
            color=sidebar.color),
        background=sidebar.background,
        position='fixed',
        top=px(0),
        min_height='100%',
        width=sidebar.width,
        z_index=810)

    # LEFT SIDEBAR OPEN
    css('.sidebar-open-left',
        css(' .sidebar',
            Transform(0, 0)),
        css(' .overlay',
            display='block'),
        css(' .navbar-side',
            display='none'),
        css(' .sidebar-page, .sidebar-navbar > nav',
            Transform(sidebar.width, 0),
            Transition('all', trans.duration, trans.easing))
        )

    css('.sidebar-fixed',
        position='fixed')

    # IMAGE in the navbar-panel
    css('.sidebar',
        css(' .nav-panel',
            Clearfix(),
            css(' .image > img',
                height=navbar.small_height-px(20),
                margin=spacing(10, 5)),
            css(' .info',
                css(' > p',
                    margin_bottom=px(4),
                    margin_top=px(5),
                    color=sidebar.info.p.color,
                    font_size=px(11)),
                css(' > a',
                    css(' .fa',
                        margin_right=px(3)),
                    text_decoration='none',
                    padding_right=px(5),
                    font_weight=600,
                    font_size=px(15)),
                padding=spacing(5, 5, 5, 15),
                line_height=1),
            padding=spacing(3, 10),
            height=navbar.small_height,
            background=sidebar.info.background),
        css(' .sidebar-menu',
            css(' > li',
                css(' > .treeview-menu',
                    background=sidebar.info.background),
                css('.active > a',
                    color=sidebar.link.color,
                    background=sidebar.link.background,
                    border_left_color=sidebar.link.color),
                css(' > a',
                    css(':hover',
                        color=sidebar.link.color,
                        background=sidebar.link.background,
                        border_left_color=sidebar.link.color),
                    margin_right=px(1),
                    border_left='3px solid transparent',
                    font_size=px(15)),
                css('.header',
                    background=sidebar.link.background,
                    color=sidebar.link.color)),
            css(' .treeview-menu',
                Transition('max-height',
                           trans.duration, 'ease-out'),
                css(' > li',
                    css('.active > a',
                        color=sidebar.link.color),
                    css(' > a',
                        css(':hover',
                            color=sidebar.link.color),
                        color=sidebar.info.p.color)),
                css('.active',
                    Transition('max-height',
                               trans.duration, 'ease-in'),
                    max_height=px(sidebar.menu.max_height),
                    opacity=1,
                    height='100%'),
                css(' .treeview-menu',
                    padding_left=px(20)),
                css(' > li',
                    css(' > a',
                        css(' > .fa',
                            width=px(20)),
                        css(' > .fa-angle-left, > .fa-angle-down',
                            width='auto'),
                        padding=spacing(5, 5, 5, 18),
                        display='block',
                        font_size=px(14)),
                    margin=px(0)),
                max_height=px(0),
                list_style='none',
                padding=px(0),
                margin=px(0),
                padding_left=px(5),
                opacity=0,
                height=px(0)),
            css(' li',
                css('.active',
                    css(' > a > .fa-angle-left',
                        Transform('all', 'rotate(-90deg)'))),
                css('.header',
                    padding=spacing(5, 25, 5, 15),
                    font_size=px(12)),
                css(' .label',
                    margin_top=px(3),
                    margin_right=px(5)),
                css(' > a',
                    css(' > .fa-angle-left',
                        width='auto',
                        height='auto',
                        padding=px(0),
                        margin_right=px(10),
                        margin_top=px(3)),
                    css(' > .fa',
                        width=px(20)),
                    padding=spacing(8, 5, 8, 15),
                    display='block'),
                position='relative',
                margin=px(0),
                padding=px(0),
                width=sidebar.width),
            list_style='none',
            margin=px(0),
            padding=px(0)),
        margin_top=px(0),
        padding_bottom=px(10))

    css('.treeview .active ~ .treeview-menu',
        Transition('max-height', trans.duration, 'ease-out'),
        css('.active',
            Transition('max-height',
                       trans.duration, 'ease-in'),
            max_height=px(sidebar.menu.max_height)),
        overflow='hidden',
        max_height=px(0))

    large = media(min_width=collapse_width)

    large.css('.sidebar .nav-panel',
              css(' .image > img',
                  height=navbar.height-px(20)),
              height=navbar.height)

    large.css('.content-wrapper',
              top=px(navbar.big_height))
