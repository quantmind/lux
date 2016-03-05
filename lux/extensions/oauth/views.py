from pulsar.apps.wsgi import Router, Json, route
from pulsar import HttpRedirect

from .oauth import request_oauths


def oauth_context(request, path='/oauth/'):
    user = request.cache.user
    if user:
        oauths = []
        current = user.get_oauths()
        for name, o in request_oauths(request).items():
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
        """Dictionary of available OAuth provider
        :param request: WSGI request
        :return: a dictionary
        """
        return dict(((name, o) for name, o in request_oauths(request).items()
                     if o.available()))

    @route('<name>')
    def oauth(self, request):
        name = request.urlargs['name']
        redirect_uri = request.absolute_uri('redirect')
        p = self._oauth(request).get(name)
        authorization_url = p.authorization_url(request, redirect_uri)
        raise HttpRedirect(authorization_url)

    @route('<name>/redirect')
    def oauth_redirect(self, request):
        """View to handle the redirect from a OAuth provider

        :param request: WSGI request with url parameters to decode
        :return: response
        """
        user = request.cache.user
        name = request.urlargs['name']
        oauth = self._oauth(request).get(name)
        try:
            oauth.check_redirect_data(request)
            token = oauth.access_token(request, redirect_uri=request.uri)
            token = dict(token)
        except Exception as exc:
            request.logger.exception('Could not obtain access_token')
            url = request.config.get('LOGIN_URL', '/')
            raise HttpRedirect(url) from exc

        access_token = oauth.save_token(request, token)
        api = oauth.api(http=request.http, **token)
        user_data = api.user()
        # User not authenticated
        if not user.is_authenticated():
            oauth.create_or_login_user(request, user_data, access_token)
        else:
            oauth.associate_token(request, user_data, user, access_token)
        raise HttpRedirect('/')

    @route('<name>/remove', method='post')
    def oauth_remove(self, request):
        user = request.cache.user
        if user.is_authenticated():
            name = request.urlargs['name']
            removed = user.remove_oauth(name)
            return Json({'success': removed}).http_response(request)
