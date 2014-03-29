from string import Template

from pulsar import ImproperlyConfigured

__all__ = ['register_template_engine', 'template_engine']

template_engines = {}


def template_engine(name):
    engine = template_engines.get(name)
    if engine is None:
        raise ImproperlyConfigured('Template engine %s not available' %
                                   name)
    return engine


def register_template_engine(name, engine):
    template_engines[name] = engine


def render(text, context):
    return Template(text).safe_substitute(context)


register_template_engine('python', render)
