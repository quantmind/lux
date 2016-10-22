from collections import OrderedDict

from pulsar import HttpRedirect, Http404

from lux.core import HtmlRouter
from lux.forms import ActionsRouter
from lux.extensions.admin import grid


class UserSettings(ActionsRouter):
    """HTML router for user and organisations related views
    """
    default_action = 'profile'

    action_config = OrderedDict((
        ('profile', {
            'link': 'Profile',
            'form': 'user-profile',
            'model': 'user',
            'target': {
                "action": "update"
            }
        }),
        ('change-password', {
            'link': 'Password change',
            'form': 'change-password'
        }),
        ('tokens', {
            'link': 'Tokens',
            'title': 'Personal access tokens',
            'model': 'user',
            'target': {
                'path': '/tokens'
            }
        }),
        ('organisations', {
            'link': 'Organisations',
            'html': '<fluid-userorgs></fluid-userorgs>'
        }),
        ('tokens/new', {
            'form': 'new-token',
            'model': 'user',
            'target': {
                'path': '/tokens'
            }
        }),
        ('organisations/new', {
            'form': 'create-organisation',
            'model': 'organisations'
        }),
    ))

    def get(self, request):
        if not request.cache.user.is_authenticated():
            raise HttpRedirect(request.config['LOGIN_URL'])
        return super().get(request)

    def action_tokens(self, request, context):
        return grid({'target': context.get('target')})


class OrgSettings(ActionsRouter):
    """HTML router for user-related views
    """
    default_action = 'profile'

    action_config = OrderedDict((
        ('profile', {
            'link': 'Profile',
            'form': 'organisation',
            'model': 'organisation',
            'target': {
                "action": "update"
            }
        }),
        ('tokens', {
            'link': 'Tokens',
            'title': 'Personal access tokens',
            'model': 'user',
            'target': {
                'path': '/tokens'
            }
        }),
        ('members', {
            'link': 'Members',
            'html': '<fluid-userorgs></fluid-userorgs>'
        }),
        ('tokens/new', {
            'form': 'new-token',
            'model': 'user',
            'target': {
                'path': '/tokens'
            }
        }),
        ('organisations/new', {
            'form': 'create-organisation',
            'model': 'organisations'
        }),
    ))

    def get(self, request):
        if request.cache.page_entity.type == 'user':
            raise Http404
        return super().get(request)

    def action_tokens(self, request, context):
        return grid({'target': context.get('target')})

    def context(self, request):
        return {'organisation': request.cache.page_entity}


class OrgApplication(ActionsRouter):
    pass


class UserView(HtmlRouter):

    def __init__(self, orgs=False):
        super().__init__('<username>')
        if orgs:
            self.add_child(OrgSettings('settings'))
            self.add_child(OrgApplication('<application>'))

    def response_wrapper(self, callable, request):
        try:
            username = request.urlargs['username']
            odm = request.app.odm()
            with odm.begin() as session:
                q = session.query(odm.entity).filter_by(username=username)
                request.cache.page_entity = q.one()
        except Exception:
            raise self.SkipRoute
        return callable(request)

    def get_html(self, request):
        app = request.app
        if request.cache.page_entity.type == 'user':
            return app.template('user/user-home.html')
        else:
            return app.template('user/org-home.html')

    def context(self, request):
        return {'user_page': request.cache.page_entity}
