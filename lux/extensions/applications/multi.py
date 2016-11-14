import string
import json
from asyncio import get_event_loop
from collections import namedtuple

from sqlalchemy.orm.exc import NoResultFound

from pulsar import Http404
from pulsar.apps.wsgi import wsgi_request

from lux.core import app_attribute, extend_config, execute_from_config
from lux.utils.crypt import generate_secret
from lux.extensions import rest
from lux.utils.crypt import create_token


KEY = '__multi_app__'
xchars = string.digits + string.ascii_lowercase
multi_apps = namedtuple('multi_apps', 'ids names domains')


class AppDomain:

    def __init__(self, app_domain):
        self.id = app_domain.id.hex
        self.name = app_domain.name
        self.domain = app_domain.domain
        self.config = dict(app_domain.config or ())
        self.app = None

    def __repr__(self):
        return self.domain or self.name

    def request(self, request, api_url):
        if not self.app:
            self.app = self._build(request.app, api_url)
        return self.app(request.environ, request.cache.start_response)

    def _build(self, main, api_url):
        config = dict(default_config(main))
        config.update(
            SESSION_COOKIE_NAME='%s-app' % self.name,
            HTML_TITLE=self.name
        )
        config.update(self.config)
        config.update(
            APP_NAME=self.name,
            API_URL=api_url
        )
        application = execute_from_config(
            'lux.extensions.applications.app',
            argv=['serve'],
            config=config,
            cmdparams=dict(
                start=False,
                get_app=True
            )
        )
        return application


class ApiClient(rest.ApiClient):

    def __init__(self, app):
        super().__init__(app)
        # netloc = urlparse(app.config['API_URL']).netloc
        # for api in app.apis:
        #     if api.netloc == netloc:
        #         self.local_apps[netloc] = app


class MultiBackend:
    """If used, this should be the first backend
    """

    def request(self, request):
        #
        # First time here
        if not request.cache.x_runtime:
            loop = get_event_loop()
            request.cache.x_count = 0
            request.cache.x_runtime = loop.time()
            request.response['X-Request-ID'] = generate_secret(32, xchars)
        else:
            request.cache.x_count += 1
            return

        app = request.app

        # listen for all events on applications model
        channels = app.channels
        channels.register(
            app.config['CHANNEL_DATAMODEL'], 'applications.*', reload_app(app)
        )

        # Get the root application
        root = get_application(app, id=app.config['MASTER_APPLICATION_ID'])
        # The root domain is not specified - cannot use multiapp
        if not root.domain:
            return

        host = request.get_host().split(':', 1)[0]
        multi = root.domain.split('.')
        bits = host.split('.')

        try:
            if len(bits) == 3 and bits[-2:] == multi[-2:]:
                name = bits[0]
                if name == 'api':
                    return
                app_domain = get_application(app, name=name)
            else:
                app_domain = get_application(app, domain=host)
        except Http404:
            return

        api_url = '%s://api.%s' % (request.scheme, '.'.join(multi[-2:]))
        return app_domain.request(request, api_url)

    def response(self, response):
        request = wsgi_request(response.environ)
        if request.cache.x_count > 0:
            request.cache.x_count -= 1
        else:
            loop = get_event_loop()
            runtime = loop.time() - request.cache.x_runtime
            request.response['X-Runtime'] = '%.6f' % runtime


@app_attribute
def default_config(app):
    """Build the default config for applications
    """
    config = {}
    if app.config['SETTINGS_DEFAULT_FILE']:
        with open(app.config['SETTINGS_DEFAULT_FILE']) as fp:
            extend_config(config, json.load(fp))
    config['EXTENSIONS'] = [
        'lux.extensions.base'
    ]
    return config


def get_application(app, id=None, name=None, domain=None):
    admin_id = app.config['MASTER_APPLICATION_ID']
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


@app_attribute
def reload_app(app):

    def _reload_app(channel, event, data):
        """Reload application
        """
        if data:
            name = data.get('name')
            app_domains = multi_applications(app)
            app_domain = app_domains.names.pop(name, None)
            if app_domain:
                app_domains.domains.pop(app_domain.domain, None)
                app_domains.ids.pop(app_domain.id.hex, None)
                app.logger.warning('reload application %s', name)
            # if domain:
            #     check_certificate(app, domain)

    return _reload_app


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

    # add app_domain object to the cache
    app_domains = multi_applications(app)
    app_domain = AppDomain(app_domain)
    app_domains.names[app_domain.name] = app_domain
    app_domains.ids[app_domain.id] = app_domain.name
    if app_domain.domain:
        app_domains.domains[app_domain.domain] = app_domain.name
    return app_domain


def _create_admin_app(app):
    id = app.config['MASTER_APPLICATION_ID']
    name = app.config['APP_NAME']
    token = create_token()

    odm = app.odm()
    with odm.begin() as session:
        session.add(odm.appdomain(id=id, name=name, token=token))
