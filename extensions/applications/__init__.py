"""Multi application extension.
"""
from lux.core import LuxExtension, Parameter
from lux.utils.countries import common_timezones, country_names

from .rest import ApplicationCRUD
from .auth import AuthBackend
from .multi import MultiBackend
from .multiplugins import has_plugin, plugins, Plugin
from .info import Info, api_info_routes


__all__ = [
    'AuthBackend',
    'MultiBackend',
    'has_plugin',
    'plugins',
    'Plugin',
    'api_info_routes'
]


class Extension(LuxExtension):
    _config = (
        Parameter('MASTER_APPLICATION_ID', None,
                  "Unique ID of the Master application. The master application"
                  " is assumed by default when no header or JWT is available"),
        Parameter('APPLICATION_ID', None,
                  "Unique ID of application. Required for client applications"
                  " but not by the API. Added to the JWT payload"),
        Parameter('API_INFO_URL', 'info',
                  "Url for information routes"),
        Parameter('SETTINGS_DEFAULT_FILE', None,
                  'Path to the json files containing default settings '
                  'for multi applications')
    )

    def on_config(self, app):
        multi = app.config.get('APP_MULTI')
        if not multi:
            # API domain
            self.require(app, 'lux.extensions.auth')
            app.add_events(('on_multi_app',))
            plugins(app).register(
                'admin',
                Plugin(extensions='lux.extensions.admin')
            )
        else:
            app.providers['Api'] = multi.api_client

    def on_multi_app(self, app, config):
        for plugin in plugins(app):
            if has_plugin(app, plugin, config):
                plugin.on_config(config)

    def on_jwt(self, app, request, payload):
        app_id = app.config['APPLICATION_ID']
        if app_id:
            payload['id'] = app_id

    def api_sections(self, app):
        yield ApplicationCRUD()
        if app.config['API_INFO_URL']:
            yield Info(app.config['API_INFO_URL'])
            routes = api_info_routes(app)
            routes['timezones'] = lambda r: common_timezones
            routes['countries'] = lambda r: country_names

    def on_query(self, app, query):
        if query.model.field('application_id'):
            app_id = self._app_id(query.request)
            if not app_id:
                app.logger.error('Application model query without app ID')
            else:
                query.filter(application_id=app_id)

    def on_before_flush(self, app, session):
        app_id = self._app_id(session.request)
        for instance in session.new:
            if 'application_id' in instance._sa_class_manager:
                if not app_id:
                    app_id = getattr(instance, 'application_id', None)
                    model = instance.__class__.__name__.lower()
                    if not app_id:
                        app.logger.error(
                            'creating %s %s without app ID', instance, model)
                    else:
                        app.logger.warning(
                            'creating %s %s for app %s',
                            instance, model, app_id
                        )
                else:
                    instance.application_id = app_id

    def _app_id(self, request):
        if request:
            user = request.cache.user
            return user.application_id if user else None
