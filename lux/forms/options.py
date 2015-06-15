from .errors import ValidationError


__all__ = ['Options', 'OptionGroup']


class Options(object):
    '''Manage group of options for a :class:`.ChoiceField`
    '''
    def __init__(self, options):
        self._choices = options or ()

    def all(self, form=None):
        choices = self._choices
        if hasattr(self._choices, '__call__'):
            choices = choices(form)
        return choices

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
        choices = set((c[0] if isinstance(c, tuple) else c
                       for c in self.all(bfield.form)))
        for v in values:
            if v not in choices:
                raise ValidationError('%s is not a valid choice' % v)
        return values


class OptionGroup(Options):

    def __init__(self, name, options):
        self.name = name
        self._choices = options
