import re
from urllib.parse import urljoin

from pulsar.apps.wsgi import Router

from apispec import Path, APISpec
from apispec import utils

from .schema import api_schema


RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')


def register_api_spec(app, cfg):
    schema = api_schema.load(cfg)
    title = cfg.get('TITLE')
    if title:
        spec = APISpec(title,
                       version=cfg.get('VERSION'),
                       plugins=cfg.get('SPEC_PLUGINS'))
        spec = APISpec(cfg.get('TITLE'),
                       version=cfg.get('VERSION'),
                       plugins=cfg.get('SPEC_PLUGINS'))
        spec.app = app

    app.api_spec = spec


def setup(spec):
    """Setup for the plugin."""
    spec.register_path_helper(path_from_view)


def pulsarpath2openapi(path):
    """Convert a Flask URL rule to an OpenAPI-compliant path.
    :param str path: Flask path template.
    """
    return RE_URL.sub(r'{\1}', path)


def path_from_view(spec, view, **kwargs):
    """Path helper that allows passing a pulsar Routers"""
    if not isinstance(view, Router):
        return
    path = pulsarpath2openapi(view.rule)
    app = spec.app
    app_root = app.config['API_URL'] or '/'
    path = urljoin(app_root.rstrip('/') + '/', path.lstrip('/'))
    operations = utils.load_operations_from_docstring(view.__doc__)
    path = Path(path=path, operations=operations)
    return path


class Response:

    def __init__(self, status_code, doc):
        self.status_code = status_code
        self.doc = doc


class apidoc:
    response = Response

    def __init__(self, doc=None, responses=None):
        self.doc = doc or ''
        self.responses = responses

    def __call__(self, handler):
        handler.__openapi__ = self
        return handler
