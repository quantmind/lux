import lux
from lux import Parameter

from .templates import DEFAULT_TEMPLATES


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('PAGE_TEMPLATES', DEFAULT_TEMPLATES,
                  'A list of functions to perocess metadata'),
        Parameter('METADATA_PROCESSORS', [],
                  'A list of functions to perocess metadata'),
        Parameter('STATIC_LOCATION', 'build',
                  'Directory where static site is created'),
        Parameter('STATIC_SITEMAP', {},
                  'Dictionary of contents for the site'),
        Parameter('EXTRA_FILES', (),
                  'List/tuple of additional files to copy to the '
                  'STATIC_LOCATION')
               ]
