'''Third party Authentication providers and APIs.

THis extension facilitates the login via OAuth providers,
Open Graph Protocol for social graphs and twitter cards (for example),
additional api a provider can have (google analytics for example).
'''
from functools import partial

import lux
from lux import Parameter

from . import dropbox
from . import facebook
from . import github
from . import google
from . import linkedin
from . import twitter


from .oauth import oauth_parameters, get_oauths
from .views import OAuthRouter, oauth_context


class Extension(lux.Extension):

    _config = [Parameter('OAUTH_PROVIDERS', None,
                         'Dictionary of dictionary of OAuth providers')]

    def on_html_document(self, app, request, doc):
        if get_oauths(request):
            doc.before_render(self.add_meta_tags)

    def add_meta_tags(self, request, doc):
        if request:
            oauth = request.cache.oauths
            for provider in oauth.values():
                provider.add_meta_tags(request, doc)
