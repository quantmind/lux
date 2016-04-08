from itertools import chain

from lux.core import LuxCommand, Setting


class Command(LuxCommand):
    help = "Show parameters."
    option_list = (
        Setting('extensions',
                nargs='*',
                desc='Extensions to display parameters from.'),
    )

    def run(self, options, **params):
        display = options.extensions
        config = self.app.config
        extensions = self.app.extensions
        for ext in chain([self.app], extensions.values()):
            if display and ext.meta.name not in display:
                continue
            if ext.meta.config:
                self.write('\n%s' % ext.meta.name)
                self.write('#=====================================')
            for key, value in ext.sorted_config():
                self.write('%s: %s' % (key, config[key]))
