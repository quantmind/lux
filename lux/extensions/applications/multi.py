import string
from asyncio import get_event_loop
from collections import namedtuple
from lux.utils.crypt import get_random_string

from sqlalchemy.orm.exc import NoResultFound

from pulsar import Http404
from pulsar.apps.wsgi import wsgi_request

from lux.core import app_attribute
from lux.utils.crypt import create_token


KEY = '__multi_app__'
xchars = string.digits + string.ascii_lowercase
multi_apps = namedtuple('multi_apps', 'ids names domains')


class Multi:

    def request(self, request):
        #
        # First time here
        if not request.cache.x_runtime:
            loop = get_event_loop()
            request.cache.x_count = 0
            request.cache.x_runtime = loop.time()
            request.response['X-Request-ID'] = get_random_string(32, xchars)
        else:
            request.cache.x_count += 1
            return

        app = request.app

        # listen for all events on applications model
        channels = app.channels
        channels.register('applications', '*', reload_app)

        root = get_application(app, id=app.config['ADMIN_APPLICATION_ID'])
        # The root domain is not specified - cannot use multiapp
        if not root.domain:
            return

            # This is the root application
        host = request.get_host().split(':', 1)[0]

        if host == root.domain:
            return

        multi = root.domain.split('.')
        bits = host.split('.')

        try:
            if len(bits) == 3 and bits[-2:] == multi[-2:]:
                app_domain = get_application(app, name=bits[0])
            else:
                app_domain = get_application(app, domain=host)
        except Http404:
            request.response.content_type = 'text/html'
            raise

        return app_domain.request(request)

    def response(self, response):
        request = wsgi_request(response.environ)
        if not request.cache.x_count > 0:
            request.cache.x_count -= 1
        else:
            loop = get_event_loop()
            runtime = loop.time() - request.cache.x_runtime
            request.response['X-Runtime'] = '%.6f' % runtime


def get_application(app, id=None, name=None, domain=None):
    admin_id = app.config['ADMIN_APPLICATION_ID']
    if not admin_id:
        raise Http404

    app_domain = None
    app_domains = multi_applications(app)

    if id:
        name = app_domains.ids.get(id)
        if not name:
            try:
                app_domain = _get_app_domain(app, id=id)
            except Http404:
                if id == admin_id:
                    _create_admin_app(app)
                    app_domain = _get_app_domain(app, id=id)
                else:
                    raise

    elif domain:
        name = app_domains.domains.get(domain)
        if not name:
            try:
                app_domain = _get_app_domain(app, domain=domain)
            except Http404:
                pass

    if not app_domain:
        if not name:
            raise Http404
        app_domain = app_domains.names.get(name)
        if not app_domain:
            app_domain = _get_app_domain(app, name=name)

    return app_domain


def reload_app(channel, event, data):
    """Reload application
    """
    if data:
        app = channel.app
        name = data.get('name')
        apps = multi_applications(app)
        if apps.names.pop(name, None):
            app.logger.warning('reload application %s', name)
        domain = data.get('domain')
        if apps.domains.pop(domain, None):
            app.logger.warning('reload application domain %s', domain)
        # if domain:
        #     check_certificate(app, domain)


@app_attribute
def multi_applications(app):
    return multi_apps({}, {}, {})


def _get_app_domain(app, **filters):
    odm = app.odm()
    with odm.begin() as session:
        try:
            app_domain = session.query(odm.appdomain
                                       ).filter_by(**filters).one()
        except NoResultFound:
            raise Http404 from None

    app_domains = multi_applications(app)
    app_domains.names[app_domain.name] = app_domain
    app_domains.ids[app_domain.id] = app_domain.name
    if app.domain:
        app_domains.fomains[app_domain.domain] = app_domain.name
    return app_domain


def _create_admin_app(app):
    id = app.config['ADMIN_APPLICATION_ID']
    name = app.config['APP_NAME']
    token = create_token()

    odm = app.odm()
    with odm.begin() as session:
        session.add(odm.appdomain(id=id, name=name, token=token))
