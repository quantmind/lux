from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.application import Sphinx

from ..builder import normpath


class LuxSphinx(Sphinx):

    def __init__(self, app, *args, **kwargs):
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

    def handle_page(self, pagename, addctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        ctx = self.globalcontext.copy()
        # current_page_name is backwards compatibility
        ctx['pagename'] = ctx['current_page_name'] = pagename
        default_baseuri = self.get_target_uri(pagename)
        # in the singlehtml builder, default_baseuri still contains an #anchor
        # part, which relative_uri doesn't really like...
        default_baseuri = default_baseuri.rsplit('#', 1)[0]

        def pathto(otheruri, resource=False, baseuri=default_baseuri):
            if resource and '://' in otheruri:
                # allow non-local resources given by scheme
                return otheruri
            elif not resource:
                otheruri = self.get_target_uri(otheruri)
            #uri = relative_uri(baseuri, otheruri) or '#'
            uri = '#'
            return uri
        ctx['pathto'] = pathto
        ctx['hasdoc'] = lambda name: name in self.env.all_docs
        if self.name != 'htmlhelp':
            ctx['encoding'] = encoding = self.config.html_output_encoding
        else:
            ctx['encoding'] = encoding = self.encoding
        ctx['toctree'] = lambda **kw: self._get_local_toctree(pagename, **kw)
        #self.add_sidebars(pagename, ctx)
        ctx.update(addctx)

        self.app.emit('html-page-context', pagename, templatename,
                      ctx, event_arg)


        try:
            output = self.templates.render(templatename, ctx)
        except UnicodeError:
            self.warn("a Unicode error occurred when rendering the page %s. "
                      "Please make sure all config values that contain "
                      "non-ASCII content are Unicode strings." % pagename)
            return

        if not outfilename:
            outfilename = self.get_outfilename(pagename)
        # outfilename's path is in general different from self.outdir
        ensuredir(path.dirname(outfilename))
        try:
            f = codecs.open(outfilename, 'w', encoding, 'xmlcharrefreplace')
            try:
                f.write(output)
            finally:
                f.close()
        except (IOError, OSError) as err:
            self.warn("error writing file %s: %s" % (outfilename, err))
        if self.copysource and ctx.get('sourcename'):
            # copy the source file for the "show source" link
            source_name = path.join(self.outdir, '_sources',
                                    os_path(ctx['sourcename']))
            ensuredir(path.dirname(source_name))
            copyfile(self.env.doc2path(pagename), source_name)
