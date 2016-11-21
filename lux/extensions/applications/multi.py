import string
import json
from asyncio import get_event_loop
from collections import namedtuple
from urllib.parse import urlparse

from sqlalchemy.orm.exc import NoResultFound

from pulsar import Http404
from pulsar.apps.wsgi import wsgi_request

from lux.core import app_attribute, extend_config, execute_from_config
from lux.utils.crypt import generate_secret
from lux.extensions.rest import ApiClient
from lux.utils.crypt import create_token


xchars = string.digits + string.ascii_lowercase
multi_apps = namedtuple('multi_apps', 'ids names domains')


class AppDomain:

    def __init__(self, app_domain):
        self.id = app_domain.id.hex
        self.name = app_domain.name
        self.domain = app_domain.domain
        self.secret = app_domain.secret
        self.config = dict(app_domain.config or ())
        self.app = None
        self.root = None
        self.api_url = None

    def __repr__(self):
        return self.domain or self.name

    def request(self, request, api_url):
        if not self.app:
            self.app = self._build(request.app, api_url)
        request.cache.multi_app = self
        return self.app(request.environ, request.cache.start_response)

    def api_client(self, app):
        """Build the api client for an application
        """
        client = ApiClient(app)
        url = urlparse(self.api_url)
        client.local_apps[url.netloc] = self.root
        return client

    def _build(self, main, api_url):
        self.root = main
        self.api_url = api_url
        config = dict(default_config(main))
        config.update(
            SESSION_COOKIE_NAME='%s-app' % self.name,
            HTML_TITLE=self.name
        )
        extend_config(config, self.config)
        config.update(
            APPLICATION_ID=self.id,
            SECRET_KEY=self.secret,
            APP_NAME=self.name,
            API_URL=api_url,
            APP_MULTI=self,
            MINIFIED_MEDIA=main.config['MINIFIED_MEDIA'],
            DEFAULT_CONTENT_TYPE="text/html"
        )
        # Fire the multi app event
        main.fire('on_multi_app', config)
        application = execute_from_config(
            main.config_module,
            argv=['serve'],
            config=config,
            cmdparams=dict(
                start=False,
                get_app=True
            )
        )
        return application


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

        return app_domain.request(request, self.api_url(request, multi))

    def response(self, response):
        request = wsgi_request(response.environ)
        if request.cache.x_count > 0:
            request.cache.x_count -= 1
        else:
            loop = get_event_loop()
            runtime = loop.time() - request.cache.x_runtime
            request.response['X-Runtime'] = '%.6f' % runtime

    def api_url(self, request, multi):
        host = request.get_host().split(':')
        url = 'api.%s' % '.'.join(multi[-2:])
        if len(host) == 2:
            url = '%s:%s' % (url, host[1])
        return '%s://%s' % (request.scheme, url)


@app_attribute
def default_config(app):
    """Build the default config for all applications
    """
    config = dict(
        AUTHENTICATION_BACKENDS=[
            "lux.extensions.applications:MultiBackend"
        ],
        EXTENSIONS=[
            'lux.extensions.base',
            'lux.extensions.rest',
            'lux.extensions.applications'
        ]
    )
    if app.config['SETTINGS_DEFAULT_FILE']:
        with open(app.config['SETTINGS_DEFAULT_FILE']) as fp:
            extend_config(config, json.load(fp))
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
                app_domains.ids.pop(app_domain.id, None)
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
