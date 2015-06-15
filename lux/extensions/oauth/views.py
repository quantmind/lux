from pulsar.apps.wsgi import Router, Json, route

from .oauth import get_oauths


def oauth_context(request, path='/oauth/'):
    user = request.cache.user
    if user:
        oauths = []
        current = user.get_oauths()
        for name, o in get_oauths(request).items():
            if o.available():
                data = {'href': path + name,
                        'name': name,
                        'fa': o.config.get('fa')}
                if name in current:
                    data['current'] = current[name]
                oauths.append(data)
        return oauths


class OAuthRouter(Router):
    '''A :class:`.Router` for the oauth authentication flow
    '''
    def _oauth(self, request):
        return dict(((name, o) for name, o in get_oauths(request).items()
                     if o.available()))

    @route('<name>')
    def oauth(self, request):
        name = request.urlargs['name']
        redirect_uri = request.absolute_uri('redirect')
        p = self._oauth(request).get(name)
        authorization_url = p.authorization_url(request, redirect_uri)
        return request.redirect(authorization_url)

    @route('<name>/redirect')
    def oauth_redirect(self, request):
        user = request.cache.user
        name = request.urlargs['name']
        p = self._oauth(request).get(name)
        token = p.access_token(request, request.url_data,
                               redirect_uri=request.uri)
        if not user.is_authenticated():
            user = p.create_user(token)
            user = request.app.auth_backend.login(request, user)
        else:
            user = p.create_user(token, user)
        return request.redirect('/%s' % user.username)

    @route('<name>/remove', method='post')
    def oauth_remove(self, request):
        user = request.cache.user
        if user.is_authenticated():
            name = request.urlargs['name']
            removed = user.remove_oauth(name)
            return Json({'success': removed}).http_response(request)
