import lux


class Command(lux.Command):
    help = "Simply return the application."

    def __call__(self, options, **params):
        self.app.thread_pool = False
        self.app.config['GREEN_POOL'] = 0
        datastores = self.app.config.get('DATASTORE')
        if datastores:
            for k, v in datastores.items():
                v = v.replace('+green', '')
                datastores[k] = v
        return super().__call__(options, **params)

    def run_until_complete(self, options, **params):
        return self.app
