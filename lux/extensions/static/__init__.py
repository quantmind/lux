'''Static site generator

**Requirements**: :mod:`lux.extensions.base`

'''
import lux
from lux import Parameter

from .templates import DEFAULT_TEMPLATE
from .builder import Content


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('STATIC_TEMPLATE', DEFAULT_TEMPLATE,
                  'Default static template'),
        Parameter('SOURCE_SUFFIX', 'md',
                  'The default suffix of source filenames'),
        Parameter('METADATA_PROCESSORS', [],
                  'A list of functions to perocess metadata'),
        Parameter('STATIC_LOCATION', 'build',
                  'Directory where static site is created'),
        Parameter('STATIC_SITEMAP', {},
                  'Dictionary of contents for the site'),
        Parameter('EXTRA_FILES', (),
                  'List/tuple of additional files to copy to the '
                  'STATIC_LOCATION'),
        Parameter('MD_EXTENSIONS', [],
                  'List/tuple of makrdown extensions')
               ]
