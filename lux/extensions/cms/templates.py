'''Some useful templates
'''
from lux.extensions.sitemap import Navigation

from .grid import PageTemplate, Grid, CmsContext, Context, Template


fixed_footer = Template(
    Grid(CmsContext('footer', all_pages=True), fixed=True),
    tag='div', id='page-footer')


float_footer = Grid(
    CmsContext('footer', all_pages=True),
    id='page-footer')


fixed_navigation = Template(
    Grid(Navigation(), fixed=True),
    tag='div', cn='navbar inverse')


float_navigation = Grid(Navigation(), cn='navbar inverse')


nav_page = PageTemplate(
    float_navigation,
    Template(Grid(CmsContext('content')),
             tag='div', id='page-main'),
    float_footer,
    key='Navigation-Content-Footer-Fluid')


nav_page_fixed = PageTemplate(
    fixed_navigation,
    Template(Grid(CmsContext('content'), fixed=True),
             tag='div', id='page-main'),
    fixed_footer,
    key='Navigation-Content-Footer-Fixed')


center_page = PageTemplate(
    Grid(Navigation(), cn='navbar inverse'),
    Context('this', tag='div', cn='center-page'),
    fixed_footer,
    key='Navigation-Center')
