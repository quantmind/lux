import string
from datetime import date
from collections import Mapping

import jinja2

from pulsar import ImproperlyConfigured

from lux.utils.date import iso8601

SKIP = object()
numbers = (int, float)
template_engines = {}


def register_template_engine(cls):
    cls.name = cls.__name__.lower()
    template_engines[cls.name] = cls()
    return cls


def template_engine(app, name):
    cache = '_template_engine_%s' % name
    engine = getattr(app, cache, None)
    if engine is None:
        engine = template_engines.get(name)
        if engine is None:
            raise ImproperlyConfigured('Template engine %s not available'
                                       % name)
        engine.configure(app)
        setattr(app, cache, engine)
    return engine


def render_data(app, value, render, context):
    """Safely render a data structure
    """
    if isinstance(value, Mapping):
        return dict(_render_dict(app, value, render, context))
    elif isinstance(value, (list, tuple)):
        return [render_data(app, v, render, context) for v in value]
    elif isinstance(value, date):
        return iso8601(value)
    elif hasattr(value, '__call__'):
        try:
            return value(app)
        except Exception:
            return SKIP
    elif isinstance(value, str):
        return render(value, context)
    elif value is None or isinstance(value, numbers):
        return value
    else:
        return SKIP


def _render_dict(app, d, render, context):
    for k, v in d.items():
        v = render_data(app, v, render, context)
        if v is not SKIP:
            yield k, v


class Template(str):
    """Mark a string to be a template
    """
    def __new__(cls, template=None):
        if isinstance(template, Template):
            return template
        else:
            return super().__new__(cls, template or '')

    def render(self, app, context, engine=None):
        rnd = app.template_engine(engine)
        return rnd(self, context)


class TemplateEngine:

    def __call__(self, text, context):
        raise NotImplementedError

    def configure(self, app):
        pass


@register_template_engine
class Python(TemplateEngine):

    def __call__(self, text, *args, **kwargs):
        context = dict(*args, **kwargs)
        return string.Template(text).safe_substitute(context)


@register_template_engine
class Jinja2(TemplateEngine):

    def __call__(self, text, *args, **kwargs):
        return jinja2.Template(text).render(*args, **kwargs)

    def configure(self, app):
        pass
