'''
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


from .oauth import oauth_parameters, oauths


class Extension(lux.Extension):

    _config = [Parameter('OAUTH_PROVIDERS', None,
                         'Dictionary of dictionary of OAuth providers')]

    def on_html_document(self, app, request, doc):
        cfg = request.config.get('OAUTH_PROVIDERS')
        if isinstance(cfg, dict):
            o = oauths(cfg)
            if o:
                request.cache.oauths = o
                doc.before_render(self.add_meta_tags)

    def add_meta_tags(self, request, doc):
        if request:
            oauth = request.cache.oauths
            for provider in oauth.values():
                provider.add_meta_tags(request, doc)

