from pulsar.utils.html import plural

from lux.core import LuxCommand, Setting


class Command(LuxCommand):
    option_list = (
        Setting('dryrun', ('--dryrun',),
                action='store_true',
                default=False,
                desc=("It does not remove any data, instead it displays "
                      "the number of models which could be removed")),
        Setting('apps', nargs='*', desc='label label.name ...')
    )
    help = "Flush models in the data server."

    def run(self, options, interactive=True):
        dryrun = options.dryrun
        odm = self.app.odm()
        self.write('\nFlush model data\n')
        apps = options.apps or None
        managers_count = odm.flush(include=apps, dryrun=True)
        if not managers_count:
            return self.write('Nothing done. No models selected')
        if not dryrun:
            self.write('\nAre you sure you want to remove these models?\n')
        for manager, N in sorted(managers_count,
                                 key=lambda x: x[0]._meta.table_name):
            self.write('%s - %s' % (manager, plural(N, 'model')))
        #
        if dryrun:
            self.write('\nNothing done. Dry run')
        else:
            self.write('')
            yn = input('yes/no : ') if interactive else 'yes'
            if yn.lower() == 'yes':
                managers_count = odm.flush(include=apps)
                for manager, removed in sorted(
                        managers_count, key=lambda x: x[0]._meta.table_name):
                    N = plural(removed, 'model')
                    self.write('{0} - removed {1}'.format(manager, N))
            else:
                self.write('Nothing done.')
