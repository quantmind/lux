'''Some useful templates
'''
from lux.extensions.sitemap import Navigation

from .grid import PageTemplate, Grid, CmsContext, Context, Template


fixed_footer = Template(
    Grid(CmsContext('footer', all_pages=True), fixed=True),
    tag='div', cn='footer')


float_footer = Grid(CmsContext('footer', all_pages=True), cn='footer')


fixed_navigation = Template(
    Grid(Navigation(), fixed=True),
    tag='div', cn='navbar inverse')


float_navigation = Grid(Navigation(), cn='navbar inverse')


nav_page = PageTemplate(
    float_navigation,
    Grid(CmsContext('content')),
    float_footer,
    key='Navigation-Content-Footer-Fluid')


center_page = PageTemplate(
    Grid(Navigation(), cn='navbar inverse'),
    Context('this', tag='div', cn='center-page'),
    fixed_footer,
    key='Navigation-Center')


Dialog = Template(
    Template(Context('title', tag='h3'), tag='div', cn='hd'),
    Template(Context('body', tag='div'), tag='div', cn='bd'))
