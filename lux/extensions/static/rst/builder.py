import os

from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.osutil import ensuredir
from sphinx.application import Sphinx

from ..builder import normpath
from ..contents import Content


class SphinxContent(Content):

    def __init__(self, app, ctx):
        content_type = 'text/html'
        meta = ctx.get('meta') or {}
        super(SphinxContent, self).__init__(app, content_type=content_type)


class LuxSphinx(Sphinx):

    def __init__(self, app, *args, **kwargs):
        self.data = []
        self.lux = app
        super(LuxSphinx, self).__init__(*args, **kwargs)

    def _init_builder(self, buildername):
        self.builder = LuxBuilder(self)
        self.emit('builder-inited')


class LuxBuilder(StandaloneHTMLBuilder):
    name = 'lux'

    def get_target_uri(self, docname, typ=None):
        if docname.startswith('_'):
            docname = docname[1:]
        return normpath(docname)

    def handle_page(self, pagename, addctx, *args, **kw):
        ctx = self.globalcontext.copy()
        src = '%s%s' % (pagename, self.config.source_suffix)
        src = os.path.join(self.srcdir, src)
        if os.path.isfile(src):
            ctx['src'] = os.path.join(self.srcdir, src)
        ctx['pagename'] = pagename
        ctx.update(addctx)
        self.app.data.append(ctx)
