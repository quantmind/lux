from string import Template

from pulsar import ImproperlyConfigured

__all__ = ['register_template_engine', 'template_engine']

default_engine = 'python'
template_engines = {}


def template_engine(name=None):
    name = name or default_engine
    engine = template_engines.get(name)
    if engine is None:
        raise ImproperlyConfigured('Template engine %s not available' %
                                   name)
    return engine


def register_template_engine(name, engine):
    template_engines[name] = engine


def render(text, context):
    return Template(text).safe_substitute(context) if context else text


register_template_engine(default_engine, render)
