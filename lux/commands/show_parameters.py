from itertools import chain

from pulsar import Setting

import lux


class Command(lux.Command):
    help = "Show parameters."
    option_list = (
        Setting('extensions',
                nargs='*',
                desc='Extensions to display parameters from.'),
    )

    def run(self, argv, **params):
        options = self.options(argv)
        display = options.extensions
        config = self.app.config
        extensions = self.app.extensions
        for ext in chain([self.app], extensions.values()):
            if display and ext.meta.name not in display:
                continue
            if ext.meta.config:
                self.write('\n%s' % ext.meta.name)
                self.write('#=====================================')
            for key in sorted(ext.meta.config):
                self.write('%s: %s' % (key, config[key]))
