'''\
:class:`Page` and :class:`Block` are used by djpcms to allow for
page customization on a running web page rather than during design.
The use of this features requires a backend database model to be implemented.
'''
import sys


__all__ = ['PageModel', 'MarkupMixin']


def block_htmlid(pageid, block):
    '''HTML id for a block container. Used throughout the library.'''
    return 'djpcms-block-{0}-{1}'.format(pageid, block)


class PageModel(object):
    '''Page object interface.

    .. attribute:: route

        The :class:`djpcms.Route` for this page

    The following attributes must be implemented by subclasses.

    .. attribute:: url

        The web site relative url

    .. attribute:: layout
    '''
    layout = 0
    layout = None
    inner_template = None
    grid_system = None

    @property
    def route(self):
        return Route(self.url)

    @property
    def inner_grid(self):
        try:
            return grid(self.inner_template)
        except:
            return None

    @property
    def path(self):
        return self.url

    def numblocks(self):
        grid = self.inner_grid
        if grid:
            return grid.numblocks
        else:
            return 1

    def add_plugin(self, p, block=0):
        '''Add a plugin to a block'''
        b = self.get_block(block)
        try:
            name = p.name
        except:
            name = p
        b.plugin_name = name
        b.save()
        return b

    def get_block(self, block, position=None):
        nb = self.numblocks()
        if block < 0 or block >= nb:
            raise ValueError('Page has {0} blocks'.format(nb))
        return self._get_block(block, position)

    # INTERNALS

    def _get_block(self, block, position):
        raise NotImplementedError

    def get_level(self):
        try:
            url = self.url
            if url.startswith('/'):
                url = url[1:]
            if url.endswith('/'):
                url = url[:-1]
            if url:
                bits = url.split('/')
                level = len(bits)
            else:
                level = 0
        except:
            level = 1
        return level

    def doc_type(self):
        d = self.doctype
        return htmldoc(d)

    @classmethod
    def register_tree_update(cls, tree_update):
        pass

    @classmethod
    def blocks(cls, pageobj):
        '''Iterator over block contents'''
        raise NotImplementedError()

    @classmethod
    def make_block(cls, **kwargs):
        raise NotImplementedError()


class MarkupMixin(object):

    def tohtml(self, text):
        if not text:
            return ''
        mkp = markups.get(self.markup)
        if mkp:
            handler = mkp.get('handler')
            text = handler(text)
            text = loader.mark_safe(to_string(text))
        return text
