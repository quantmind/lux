'''
An extension for managing navigation on a web site. The extension does not add
any :ref:`middleware <middleware>` to the lux WSGi handler, instead it
adds an handler to the :ref:`on_html_document event <event_on_html_document>`.
Therefore, the extension is only used when the response to a client
request has a ``text/html`` content type.

Parameters
================

.. lux_extension:: lux.extensions.sitemap


Usage
=============
This extensions is only used when the HTTP response has a ``text/html``
content type.
In this case, when the :attr:`.WsgiRequest.html_document` is accessed for the
first time, the extension, via the :meth:`~Extension.on_html_document` handler,
adds a :class:`NavigationInfo` object to the ``request.cache`` dictionary.
This object can be accessed via ``request.cache.html_navigation`` if needed.

The ``html_navigation`` can be used to render a navigation toolbar via
the :class:`Navigation` template.:

    >>> from lux.extensions.sitemap import Navigation
    >>> toolbar = Navigation()
    >>> html = toolbar.render()

This extension should be positioned, within the :setting:`EXTENSIONS` list,
before extensions which need to access the ``html_navigation`` instance
in the ``request.cache`` dictionary. Since it does not add any
wsgi middleware, it is safe to add it as the first extension.


Adding entries
~~~~~~~~~~~~~~~~~~~~

The :class:`NavigationInfo` works by looping over all wsgi middleware
which is a instance of :class:`.Router` and check if the ``navigation_visit``
method is available.

For example this router implement a 'doc' link::

    class SomeRouter(lux.Router):

        def navigation_visit(self, request, nav):
            ...

For example, in the :ref:`cms extensions <extension-cms>`, the
:class:`.EditPage` router adds links to edit or exit-editing of pages.

API
==========

Extension
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Extension
   :members:
   :member-order: bysource

NavigationInfo
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: NavigationInfo
   :members:
   :member-order: bysource

Navigation
~~~~~~~~~~~~~~~~~~

.. autoclass:: Navigation
   :members:
   :member-order: bysource

'''
import logging
from collections import namedtuple

from pulsar.apps.wsgi import Html

import lux
from lux import Router, Parameter

from .links import *
from .ui import add_css


LOGGER = logging.getLogger('lux.navigation')


def request_from_view(request, view, urlargs=None):
    urlargs = urlargs if urlargs is not None else request.urlargs
    if view == request.view and urlargs == request.urlargs:
        return request
    else:
        path = view.route.url(**urlargs)
        return RequestView(request.environ, path, view, urlargs)


def request_children(request):
    '''generator of all direct children of request'''
    parent_route = request.view.route
    level = parent_route.level + 1
    for view in request.router.routes:
        route = view.route
        if (route.level == level and
                route.breadcrumbs[:-1] == parent_route.breadcrumbs):
            yield view


def request_known_children(request):
    app_handler = request.app_handler
    if app_handler and hasattr(app_handler, 'routes'):
        parent_route = app_handler.route
        for router in app_handler.routes:
            if router.route.arguments == parent_route.arguments:
                yield router


def navigation(request, root=None, levels=None):
    '''Generator of :class:`RequestView` to include in a navigation.'''
    # view serving the request
    levels = levels or 1
    if root:
        request = request.resolve(root or request.path)
    for handler in request_known_children(request):
        in_nav = getattr(view, 'in_navigation', 0)
        if in_nav:
            req = request_from_view(request, view)
            if req.has_permissions():
                yield req


class NavigationInfo(object):
    '''Collect navigation information.

    All attributes are optional and only those available are rendered
    via the :class:`Navigation` template.

    .. attribute:: brand

        A brand name for the web site
    '''

    def __init__(self, brand=''):
        self.brand = brand
        self.primary = []
        self.secondary = []
        self.user = []
        self.search = []

    def item(self, url, text=None, icon=None, title=None, **kw):
        '''Create a :class:`.Link` object
        '''
        title = title or text
        if text and icon:
            text = ' %s' % text
        return Link(href=url, icon=icon, children=(text,), title=title, **kw)

    def load(self, request):
        '''Load navigation information from routers serving the application.
        '''
        app = request.app
        for handle in app.handler.middleware:
            if isinstance(handle, Router):
                self.add_link(request, handle)

    def add_link(self, request, handle):
        if hasattr(handle, 'navigation_visit'):
            try:
                handle.navigation_visit(request, self)
            except Exception:
                self.logger.exception('Could not add link')
        for router in handle.routes:
            self.add_link(request, router)


class Navigation(lux.Template):
    '''A :class:`.Template` which can be used to render the
    :class:`NavigationInfo` object stored in the ``request.cache``
    dictionary.
    '''
    def html(self, request, context, children, **parameters):
        if request:
            info = request.cache.html_navigation
            if info is None:
                LOGGER.warning('To use the navigation you must include '
                               'lux.extensions.sitemap in your EXTENSIONS '
                               'list')
            else:
                info.load(request)
                nav = Html(None)
                if self.parameters.layout == 'horizontal':
                    nav.addClass('inner clearfix')
                return self.layout(request, info, nav)

    def layout(self, request, info, nav):
        config = request.app.config
        template = config['NAVIGATION_TEMPLATE']
        levels = config['NAVIGATION_LEVELS']
        for name in template:
            data = getattr(info, name, None)
            if data:
                handle = getattr(self, name, None)
                if handle:
                    data = handle(request, data)
                nav.append(data)
        return nav

    def brand(self, request, data):
        link = request.app.config['NAVIGATION_BRAND_LINK']
        return Html('a', data, cn='brand', href=link)

    def main(self, request, data):
        ul = Html('ul', cn='nav')
        for link in data:
            ul.append(link)
        return ul

    def secondary(self, request, data):
        ul = Html('ul', cn='nav secondary')
        for link in data:
            ul.append(link)
        return ul

    def user(self, request, data):
        ul = Html('ul', cn='nav user')
        for link in data:
            ul.append(link)
        return ul


class Extension(lux.Extension):
    _config = [
        Parameter('NAVIGATION_LEVELS', 1, ''),
        Parameter('NAVIGATION_BRAND', '',
                  'Html string for the brand in the toolbar'),
        Parameter('NAVIGATION_BRAND_LINK', '/',
                  'The href value of the anchor which display the brand in the'
                  ' navigation toolbar'),
        Parameter('NAVIGATION_TEMPLATE',
                  ('brand', 'main', 'secondary', 'user'),
                  'Layout of the Navigation Toolbar'),
        Parameter('NAVIGATION_CLASSES', 'nav nav-list standard', '')]

    def on_html_document(self, app, request, doc):
        '''Add the ``html_navigation`` entry in the ``request.cache``.

        Loop over all Routers which have the ``navigation_visit`` method
        implemented. The ``html_navigation`` is an instance of
        :class:`NavigationInfo` and can be used to add navigation
        items as well as logos and search boxes.
        '''
        if doc.is_html:
            brand = app.config['NAVIGATION_BRAND']
            request.cache.html_navigation = NavigationInfo(brand)

    def navigation(self, request, routers, levels=None):
        '''Create an ul with links.'''
        levels = levels or self.config['NAVIGATION_LEVELS']
        ul = Html('ul', cn=self.config['NAVIGATION_CLASSES'])
        for _, router in sorted(self._ordered_nav(routers),
                                key=lambda x: x[0]):
            if router.parameters.navigation:
                try:
                    link = router.link()
                except KeyError:
                    continue
                ul.append(link)
        return ul.render(request)

    def _ordered_nav(self, routers):
        for router in routers:
            if router.parameters.navigation:
                yield router.parameters.navigation, router
