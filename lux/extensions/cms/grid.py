'''
The :mod:`lux.extensions.cms.grid` module contains several components
for creating :class:`PageTemplate` to use with the content management system.

PageTemplate
=================

.. autoclass:: PageTemplate
   :members:
   :member-order: bysource

Grid
=============

.. autoclass:: Grid
   :members:
   :member-order: bysource


Row
=============

.. autoclass:: Row
   :members:
   :member-order: bysource

Column
=============

.. autoclass:: Column
   :members:
   :member-order: bysource

CmsContext
=================

.. autoclass:: CmsContext
   :members:
   :member-order: bysource
'''
import json
from collections import Mapping

from pulsar import coroutine_return

import lux
from lux import Html, Template, Context

from .contents import apply_content


class Column(Template):
    '''A column can have one or more :class:`Block`.'''
    tag = 'div'
    classes = 'column'

    def __init__(self, *children, **params):
        self.span = params.pop('span', 1)
        super(Column, self).__init__(*children, **params)
        if self.span > 1:
            raise ValueError('Column span "%s" greater than one!' % self.span)


class Row(Template):
    '''A :class:`Row` is a container of :class:`Column` elements.
It  must contain at least one :class:`Column`.

:param column: Optional parameter which set the :attr:`column` attribute.

.. attribute:: column

    It can be either 12 or 24 and it indicates the number of column
    spans available.

    Default: 24
'''
    tag = 'div'
    columns = 24

    def __init__(self, *children, **params):
        self.columns = params.pop('columns', self.columns)
        self.classes = 'grid%s row' % self.columns
        super(Row, self).__init__(*children, **params)

    def child_template(self, child=None):
        if not isinstance(child, Column):
            child = Column(child)
        span = int(child.span * self.columns)
        child.classes += ' span%s' % span
        return child


class Grid(Template):
    '''A container of :class:`Row` or :class:`CmsContext` templates.

:parameter fixed: optional boolean flag to indicate if the grid is
    fixed (html class ``grid fixed``) or fluid (html class ``grid fluid``).
    If not specified the grid is considered fluid (it changes width when
    the browser window changes width).

A :class:`Grid` elements is usually a direct child of a :class:`PageTemplate`,
unless additional wrapping elements are used.
'''
    tag = 'div'

    def html(self, request, context, children, **kwargs):
        html = super(Grid, self).html(request, context, children, **kwargs)
        cn = 'grid fixed' if self.parameters.fixed else 'grid fluid'
        return html.addClass(cn)

    def child_template(self, child=None):
        if not isinstance(child, (Row, CmsContext)):
            child = Row(child)
        return child


class PageTemplate(Template):
    '''The main :class:`.Template` of the content management system extension.

    The template renders the inner part of the HTML ``body`` tag.
    A page template is created by including the page components during
    initialisation, for example::

        from lux.extensions.cms.grid import PageTemplate

        head_body_foot = PageTemplate(
            Row()
            Grid(CmsContext('content')),
            Grid(CmsContext('footer', all_pages=True)))
    '''
    tag = 'div'
    classes = 'cms-page'

    def __init__(self, *children, **params):
        params['role'] = 'page'
        super(PageTemplate, self).__init__(*children, **params)

    def html(self, request, context, children, **kwargs):
        html = super(PageTemplate, self).html(request, context, children,
                                              **kwargs)
        if request:
            site_contents = []
            ids = context.get('content_ids')
            if ids:
                contents = yield request.models.content.filter(id=ids).all()
                for content in contents:
                    for pos in ids.get(content.id, ()):
                        apply_content(pos, content, context)
            doc = request.html_document
            doc.head.scripts.require('cms')
        coroutine_return(html)


class CmsContext(Context):
    '''A specialised :class:`.Context` for rendering
    the dynamic content in a :class:`PageTemplate`.
    The dynamic content is retrieved from data in a backend database.

    :param all_pages: optional boolean to pass during initialisation,
        it sets the :attr:`all_pages` attribute
    '''
    tag = 'div'
    classes = 'cms-grid'

    def html(self, request, context, children, render=True, **params):
        page = request.cache.page if request else None
        if render:
            if page:
                context[self.key] = self._get_content(page, context)
            elif self.all_pages:
                pass
        return super(CmsContext, self).html(request, context, children,
                                            **params)

    @property
    def all_pages(self):
        '''When ``True``, this context is used by all pages.'''
        return self.parameters.all_pages

    def _get_content(self, page, context):
        container = Html(None)
        if 'content_ids' not in context:
            context['content_ids'] = {}
        ids = context['content_ids']
        for content in page.content.get(self.key) or ():
            template = content.get('template')
            row = Html('div', template=template)
            for content in content.get('children') or ():
                column = Html('div')
                for bc in content or ():
                    block = Html('div', template=bc.get('template'))
                    for id, html in self._contents(bc.get('children'),
                                                   context):
                        if id in ids:
                            ids[id].append(html)
                        else:
                            ids[id] = [html]
                        block.append(html)
                    column.append(block)
                row.append(column)
            container.append(row)
        return container

    def _contents(self, contents, context):
        for content in contents or ():
            id = content.get('id') if content else None
            if id:
                content_type = content['content_type']
                yield id, Html('div', id='%s-%s' % (content_type, id))
