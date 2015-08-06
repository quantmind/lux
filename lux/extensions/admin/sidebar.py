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
    sidebar.toggle.padding = 0.5*(navbar.height-sidebar.toggle.size) - px(1)
    # Style
    sidebar.background = '#2D3C4B'
    sidebar.color = '#eee'
    sidebar.toggle.border = '1px solid #ddd'
    sidebar.info.p.color = '#ccc'
    sidebar.info.background = '#425466'

    trans = sidebar.transition
    # Why this? because unitary operations don't work yet and px(0) fails
    sidebar.width_neg = px(1) - sidebar.width - px(1)
    collapse_width = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    media(min_width=collapse_width).css(
        '.navbar.navbar-static-top .navbar-nav',
        css('> li > a.sidebar-toggle',
            font_size=sidebar.toggle.size,
            line_height=sidebar.toggle.size,
            padding_top=sidebar.toggle.padding,
            padding_bottom=sidebar.toggle.padding))

    css('.fullwidth',
        width=pc(100),
        overflow_x='hidden')

    css('.sidebar-body',
        position='relative')

    css('.sidebar-page',
        position='relative',
        top=0,
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
            css(' .treeview-menu',
                Transition('height', trans.duration, 'linear'),
                css('.active',
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

    large = media(min_width=collapse_width)

    large.css('.sidebar .nav-panel',
              css(' .image > img',
                  height=navbar.height-px(20)),
              height=navbar.height)

    #  sidebar_skin(all)


def small():
    small = media(max_width=collapse_width)

    small.css('.sidebar .nav-panel',
              height=px(navbar.small_height))

    small.css('.navbar-header > .navbar-nav',
              float='left',
              margin=px(0))

    small.css('.sidebar-toggle',
              font_size=sidebar.toggle.size_small,
              padding_top='20px !important',
              height=px(navbar.small_height))

    small.css('.right-sidebar',
              css(' .navbar-static-top',
                  css(' .navbar-main',
                      float='right',
                      margin_right=px(1))))

    small.css('.sidebar-left',
              css(' .navbar-static-top',
                  css(' .navbar-main',
                      float='left',
                      margin_left=px(1))))


def sidebar_skin(all):
    '''Sidebar default skin styles
    '''
    css = all.css
    sidebar = all.variables.sidebar

    # Dark skin
    default = sidebar.skins.default
    default.border_color = '#eee'
    default.border_size = 1
    default.color = '#eee'
    default.background = '#2D3C4B'

    default.header.background = '#fff'
    default.header.color = '#eee'

    default.menu.link.color = '#fff'
    default.menu.link.background = '#263647'
    default.menu.link.border_color = '#fff'
    default.menu.section.color = '#fff'
    default.menu.section.background = '#243241'

    default.toggle.link.color = '#333'
    default.toggle.link.color_hover = '#999'
    default.toggle.link.background_hover = '#fff'

    default.treeview.background = '#3E5165'
    default.treeview.link.color = '#ccc'
    default.treeview.link.color_active = '#fff'

    if not sidebar.skin or sidebar.skin == 'default':
        skin = default
    else:
        skin = sidebar.skins[sidebar.skin]

    css('.skin',
        css(' .sidebar',
            css(' > .sidebar-menu',
                css(' > li',
                    css(' > .treeview-menu',
                        background=skin.treeview.background),
                    css('.active > a',
                        color=skin.menu.link.color,
                        background=skin.menu.link.background,
                        border_left_color=skin.menu.link.border_color),
                    css(' > a',
                        css(':hover',
                            color=skin.menu.link.color,
                            background=skin.menu.link.background,
                            border_left_color=skin.menu.link.border_color),
                        margin_right=px(1),
                        border_left='3px solid transparent',
                        font_size=px(15)),
                    css('.header',
                        background=skin.menu.section.background,
                        color=skin.menu.section.color),
                    ))),
        css(' .treeview-menu',
            css(' > li',
                css('.active > a',
                    color=skin.treeview.link.color_active),
                css(' > a',
                    css(':hover',
                        color=skin.treeview.link.color_active),
                    color=skin.treeview.link.color),
                ))
        )
