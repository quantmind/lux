from pulsar import Http404

from lux.core import LuxCommand, CommandError, Setting


class Command(LuxCommand):
    help = 'Regenerate an application token'
    option_list = (
        Setting('app_id',
                nargs='*',
                desc='Application ID'),
    )

    def run(self, options, **params):
        auth_backend = self.app.auth_backend
        request = self.app.wsgi_request(urlargs={}, app_handler=True)
        request.cache.auth_backend = auth_backend
        model = self.app.models['applications']
        app_id = options.app_id or request.config['MASTER_APPLICATION_ID']
        if not app_id:
            raise CommandError('app_id not available')
        try:
            app_domain = model.get_instance(request, id=app_id)
        except Http404:
            raise CommandError('app_id %s not available' % app_id) from None
        token = model.regenerate_token(request, app_domain)
        self.write(token)
        return token
