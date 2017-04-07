"""Multi application extension.
"""
from lux.core import LuxExtension, Parameter

from .rest import ApplicationCRUD, PluginCRUD
from .auth import AuthBackend


__all__ = [
    'AuthBackend',
    'MultiBackend',
    'has_plugin',
    'plugins',
    'Plugin'
]


class Extension(LuxExtension):
    _config = (
        Parameter('MASTER_APPLICATION_ID', None,
                  "Unique ID of the Master application. The master application"
                  " is assumed by default when no header or JWT is available"),
        Parameter('APPLICATION_ID_HEADER', 'HTTP_X_APPLICATION_ID',
                  'Header which stores the application ID'
                  )
    )

    def api_sections(self, app):
        return (
            ApplicationCRUD(),
            PluginCRUD()
        )

    def on_jwt(self, app, request, payload):
        app_id = app.config['APPLICATION_ID']
        if app_id:
            payload['id'] = app_id

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
