from lux.core import Parameter
from lux.extensions import base


CONTENT_GROUPS = {
    'site': {
        'path': '*',
        'body_template': 'home.html'
    },
    'bla': {
        'path': '/bla/',
        'body_template': 'bla.html'
    },
    'foo_id': {
        'path': '/foo/<id>',
        'body_template': 'foo.html'
    }
}


class Extension(base.Extension):
    _config = [
        Parameter('RANDOM_P', False),
        Parameter('USE_ETAGS', False, ''),
    ]
