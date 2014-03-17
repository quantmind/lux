try:
    input = raw_input
except NameError:
    pass

from pulsar import Setting

import lux


class Command(lux.Command):
    option_list = (
        Setting('apps', nargs='*', desc='app app.modelname ...'),
    )
    help = "Flush models in the data server."

    def __call__(self, argv, **params):
        return self.run_until_complete(argv, **params)

    def run(self, argv, dump=True):
        options = self.options(argv)
        models = self.app.models
        if not models:
            self.logger.info('No model registered')
        apps = options.apps or None
        managers = models.flush(include=apps, dryrun=True)
        if managers:
            print('')
            print('Are you sure you want to remove these models?')
            print('')
            for manager in sorted(managers, key=lambda x: x._meta.modelkey):
                backend = manager.backend
                print('%s from %s' % (manager._meta, backend))
            print('')
            yn = input('yes/no : ')
            if yn.lower() == 'yes':
                result = yield models.flush(include=apps)
                for manager, N in zip(managers, result):
                    print('{0} - removed {1} models'.format(manager._meta, N))
            else:
                print('Nothing done.')
        else:
            print('Nothing done. No models selected')
