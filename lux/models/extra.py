from functools import partial

from marshmallow import fields

from pulsar.utils.slugify import slugify


class Password(fields.String):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.metadata['html_type'] = 'hidden'


class Slug(fields.String):
    validation_error = ('Only lower case, alphanumeric characters and '
                        'hyphens are allowed')

    def __init__(self, *args, separator='-', **kw):
        kw.setdefault('autocorrect', 'off')
        kw.setdefault('autocapitalize', 'none')
        super().__init__(*args, **kw)
        self.validators.append(partial(slug_validator, separator))


def slug_validator(separator, value):
    return slugify(value, separator=separator) == value

