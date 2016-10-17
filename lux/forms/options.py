from enum import Enum

from .errors import ValidationError


def as_value_dict(c):
    if not isinstance(c, dict):
        c = {'value': c}
    return c


def options_from_enum(options):
    for option in options:
        yield option.name


class Options:
    '''Manage group of options for a :class:`.ChoiceField`
    '''
    def __init__(self, options):
        if isinstance(options, type) and issubclass(options, Enum):
            options = tuple(options_from_enum(options))
        self._choices = options or ()

    def all(self, form=None):
        choices = self._choices
        if hasattr(self._choices, '__call__'):
            choices = choices(form)
        options = []
        for c in choices:
            if isinstance(c, OptionGroup):
                options.extend(c)
            else:
                options.append(c)
        return options

    def get_initial(self, form=None):
        choices = self.all(form)
        if choices:
            initial = choices[0]
            if isinstance(initial, Options):
                initial = initial.get_initial(form)
            elif isinstance(initial, dict):
                initial = initial.get('value')
            elif initial and isinstance(initial, (list, tuple)):
                initial = initial[0]
            return initial

    def clean(self, values, bfield):
        choices = set()
        for c in self.all(bfield.form):
            if isinstance(c, (list, tuple)):
                c = c[0]
            elif isinstance(c, dict):
                c = c['value']
            choices.add(c)

        for v in values:
            if v not in choices:
                raise ValidationError('%s is not a valid choice' % v)
        return values


class OptionGroup:

    def __init__(self, name, options):
        self.name = name
        self._choices = options

    def __iter__(self):
        for c in self._choices:
            c = as_value_dict(c)
            c['group'] = self.name
            yield c
