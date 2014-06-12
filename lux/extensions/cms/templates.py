'''Some useful templates
'''
from lux.extensions.sitemap import Navigation
from lux import PageTemplate, GridTemplate, Context, Template

from .views import CmsContext


fixed_footer = Template(
    GridTemplate(CmsContext('footer', all_pages=True), fixed=True),
    tag='div', id='page-footer')


float_footer = GridTemplate(
    CmsContext('footer', all_pages=True),
    id='page-footer')


fixed_navigation = Template(
    GridTemplate(Navigation(), fixed=True),
    tag='div', cn='navbar inverse')


float_navigation = GridTemplate(Navigation(), cn='navbar inverse')


nav_page = PageTemplate(
    float_navigation,
    Template(GridTemplate(CmsContext('content')),
             tag='div', id='page-main'),
    float_footer,
    key='Navigation-Content-Footer-Fluid')


nav_page_fixed = PageTemplate(
    fixed_navigation,
    Template(GridTemplate(CmsContext('content'), fixed=True),
             tag='div', id='page-main'),
    fixed_footer,
    key='Navigation-Content-Footer-Fixed')


center_page = PageTemplate(
    GridTemplate(Navigation(), cn='navbar inverse'),
    Context('this', tag='div', cn='center-page'),
    fixed_footer,
    key='Navigation-Center')
