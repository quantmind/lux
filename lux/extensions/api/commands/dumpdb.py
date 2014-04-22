from io import StringIO

from pulsar import Setting

import lux


class Command(lux.Command):
    option_list = (
        Setting('apps', nargs='*',
                desc='appname appname.ModelName ...'),
        Setting('indent', ('--indent',),
                default=-1, type=int,
                desc=('Specifies the indent level to use when'
                      ' using json output.')),
        Setting('format', ('-f', '--format'),
                default='json',
                desc='The data format.'),
        Setting('target', ('-t', '--target'),
                default='stdnetdump',
                desc='Filename.'),
        Setting('listall', ('-l', '--list-all'),
                action='store_true',
                default=False,
                desc='List all supported formats and exit.'),
    )
    help = ("Output the content of registered models in the data-server into "
            "a file given an output format. If no application is passed to "
            "the positional argument list, it looks if the config dictionary "
            "contains the DUMPDB_EXTENSIONS list, otherwise it dumps all "
            "registered models.")

    def __call__(self, argv, **params):
        return self.run_until_complete(argv, **params)

    def run(self, argv, dump=True):
        options = self.options(argv)
        apps = options.apps or self.app.config.get('DUMPDB_EXTENSIONS')
        models = self.app.extensions['api'].get_router()
        if not models:
            self.logger.info('No model registered')
        else:
            fname = '%s.%s' % (options.target, options.format)
            self.logger.info('Aggregating %s data into "%s".' %
                             (options.format, fname))
            stream = StringIO()
            for model in models:
                # If the model is marked as not serializable, skip it.
                if not getattr(model, 'serializable', True):
                    continue
                model.write(stream, options.format)
        if dump:
            with open(file_name, 'w') as stream:
                serializer.write(stream)
        return serializer

    def get_models(self, apps):
        models = self.app.models()
        if apps:
            pass
        # if not getattr(model, 'serializable', True):
        #     continue
        return models

    def preprocess(self, options, queries):
        return queries

    def listall(self):
        indent = options.indent
        if indent == -1:
            indent = None
        serializer = odm.get_serializer(options.format, indent=indent)
        if options.listall:
            for name in odm.all_serializers():
                print(name)
            exit(0)
