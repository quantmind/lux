import os

from lux.core import Parameter, LuxExtension

from .models import ContentModel
from .rest import ContentCRUD
from .cms import CMS, LazyContext
from .github import GithubHook, EventHandler, PullRepo
from .files import content_location
from .views import TemplateRouter


__all__ = ['Content',
           'ContentCRUD',
           'CMS',
           'GithubHook',
           'EventHandler',
           'PullRepo',
           'LazyContext']


class Extension(LuxExtension):
    _config = [
        Parameter('CONTENT_REPO', None,
                  'Directory where content repo is located'),
        Parameter('CONTENT_LOCATION', None,
                  'Directory where content is located inside CONTENT_REPO'),
        Parameter('HTML_TEMPLATES_URL', 'templates',
                  'Base url for serving HTML templates when the default '
                  'content type is text/html. Set to None if not needed.'),
        Parameter('GITHUB_HOOK_KEY', None,
                  'Secret key for github webhook')
    ]

    def on_config(self, app):
        self.require(app, 'lux.extensions.rest')

    def middleware(self, app):
        url = app.config['HTML_TEMPLATES_URL']
        if app.config['DEFAULT_CONTENT_TYPE'] == 'text/html' and url:
            yield TemplateRouter(url, serve_only=('html', 'txt'))

    def on_loaded(self, app):
        if app.config['DEFAULT_CONTENT_TYPE'] == 'text/html':
            app.cms = CMS(app)

    def api_sections(self, app):
        location = content_location(app)
        if not location:
            return

        secret = app.config['GITHUB_HOOK_KEY']
        middleware = []
        #
        # Add github hook if the secret is specified
        if secret:
            middleware.append(GithubHook('/refresh-content',
                                         handle_payload=PullRepo(location),
                                         secret=secret))
        middleware.append(ContentCRUD('{0}/<group>',
                                      model=ContentModel(location)))
        return middleware

    def get_template_full_path(self, app, name):
        repo = content_location(app)
        if repo:
            return os.path.join(repo, 'templates', name)
        else:
            return super().get_template_full_path(app, name)
