from lux.core import LuxCommand, Setting


class Command(LuxCommand):
    option_list = (
        Setting('dryrun', ('--dryrun',),
                action='store_true',
                default=False,
                desc=("It does not remove any data, instead it displays "
                      "the number of models which could be removed")),
        Setting('models', nargs='+',
                desc='model1 model2 ... Use * to include all models')
    )
    help = "Flush models in the data servers"

    def run(self, options, interactive=True, yn='yes'):
        if options.models[0] == '*':
            models = list(self.app.models)
        else:
            models = []
            for model in options.models:
                if model in self.app.models:
                    models.append(model)
        if not models:
            return self.write('Nothing done. No models')
        #
        self.write('\nAre you sure you want to remove these models?\n')
        for model in sorted(models):
            self.write('%s' % model)
        #
        if options.dryrun:
            self.write('\nNothing done. Dry run')
        else:
            self.write('')
            yn = input('yes/no : ') if interactive else yn
            if yn.lower() == 'yes':
                request = self.app.wsgi_request()
                for model in models:
                    model = self.app.models[model]
                    with model.session(request) as session:
                        N = model.query(request, session).delete()
                        self.write('{0} - removed {1}'.format(model, N))
            else:
                self.write('Nothing done')
