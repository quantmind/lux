from string import Template

import jinja2

from pulsar import ImproperlyConfigured


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


class TemplateEngine:

    def __call__(self, text, context):
        raise NotImplementedError

    def configure(self, app):
        pass


@register_template_engine
class Python(TemplateEngine):

    def __call__(self, text, *args, **kwargs):
        context = dict(*args, **kwargs)
        return Template(text).safe_substitute(context)


@register_template_engine
class Jinja2(TemplateEngine):

    def __call__(self, text, *args, **kwargs):
        return jinja2.Template(text).render(*args, **kwargs)

    def configure(self, app):
        pass
