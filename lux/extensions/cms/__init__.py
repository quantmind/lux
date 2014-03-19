'''Content management system using Pages and blocks in pages.

**Requirements**: :mod:`lux.extensions.base`, :mod:`lux.extensions.api`

The extension add two :ref:`routers <router>` to the list of your application
middleware.

Parameters
================

.. lux_extension:: lux.extensions.cms

Usage
=======

This adds a :ref:`on_html_response <event_on_html_document>` callback
for handling the html layout. The callback is implemented via the
:class:`.CmsResponse` class.

Positioning and editing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the configuration parageter ``PAGE_EDIT_URL`` is enabled, it is
possible to edit html page layout by moving content around and adding
new content.

* A page specify a given template which in turns can have several
  (usually one or two) grid elements.
* Each ``grid`` element contain one or more ``row`` elements.
* Each ``row`` element contain one or more ``column`` elements.
* Each ``column`` element contain one or more ``block`` elements, rendered
  vertically, one after the other.
* Finally a ``block`` element contains one or more ``position`` elements which
  display a ``content``.

The ``content`` is stored in the :class:`models.Content` model.


.. _contenturl:

Site Content
~~~~~~~~~~~~~~~~~~
A special :ref:`cms content type <cms-content-type>` is the site content.
Any :ref:`Router <router>` with a ``get`` method implemented which can
respond to a request for ``text/html`` content type, can be included as site
content.

Site content can than be displayed anywhere on the web site thanks to
the content management system positioning and editing functionalities.

To include a router, one must set the attribute ``cms_content`` to a title
string used by the content management system in the drop-down selection
of site contents. For example::

  class SimpleContent(lux.Router):
      cms_content = 'A simple Hello'

      def get(self, request):
          return 'Hello!'


The :meth:`views.EditPage.content_urls` method is responsible for collecting
all valid site content to include in the drop-down selection element.


API
=========

API Extension
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Extension
   :members:
   :member-order: bysource

Routes & Hooks
~~~~~~~~~~~~~~~~~

.. automodule:: lux.extensions.cms.views

Page Components
~~~~~~~~~~~~~~~~~

.. automodule:: lux.extensions.cms.grid

Models
~~~~~~~~~~~~~

.. automodule:: lux.extensions.cms.models

'''
from pulsar import (HttpException, HttpRedirect, PermissionDenied,
                    HaltServer)
from pulsar.utils.structures import OrderedDict
from pulsar.apps.ws import WebSocket

import lux
from lux import route, Parameter
from lux.extensions import api

from .ui import add_css
from .forms import ContentForm
from .views import (EditPage, CmsRouter, PageUpdates, PageForm,
                    PageContentManager, CmsResponse, CONTENT_API_URL)
from . import templates


class Extension(lux.Extension):
    _config = [
        Parameter('PAGE_TEMPLATES', [templates.nav_page,
                                     templates.nav_page_fixed,
                                     templates.center_page],
                  'A list of Templates which can be used to render a page.'),
        Parameter('SITE_ID', None, 'The database id of the site'),
        Parameter('PAGE_EDIT_URL', 'pages',
                  'Base url for editing pages on the browser.'),
        Parameter('CREATE_PAGE_TEMPLATE', templates.center_page,
                  'Function which return an Html element to which render the '
                  'create new page form'),
        Parameter('NO_PAGE_TEMPLATE', templates.center_page,
                  'Template Page for a response on a resource without '
                  'own page')]

    def on_config(self, app):
        self.cms_response = CmsResponse()
        url = app.config['PAGE_EDIT_URL']
        if not url.endswith('/'):
            app.config['PAGE_EDIT_URL'] = '%s/' % url

    def on_loaded(self, app, handler):
        templates = app.config['PAGE_TEMPLATES']
        dtemplates = OrderedDict()
        for id, template in enumerate(app.config['PAGE_TEMPLATES'], 1):
            if not template.key:
                template.key = 'Template %s' % id
            dtemplates[template.key] = template
        app.config['PAGE_TEMPLATES'] = dtemplates
        models = app.models
        path = app.config['PAGE_EDIT_URL']
        ws = WebSocket('<id>/updates', PageUpdates())
        handler.middleware.extend((EditPage(path, models.page, ws),
                                   CmsRouter('<path:path>')))

    def on_start(self, app, server):
        if not app.config['SITE_ID']:
            raise HaltServer('SITE_ID not given. Run the '
                             '"create_site" command to get one')

    def on_html_response(self, app, request, html):
        '''Fired when an HTML response is about to be sent to the client.

        It delegates the handling of the ``html`` to the
        :class:`.CmsResponse` class.
        '''
        return self.cms_response(request, html)

    def api_sections(self, app):
        '''Add api support for ``pages`` and ``content``.'''
        yield 'Content Management System', self._api_routes(app)

    #    INTERNALS

    def _api_routes(self, app):
        models = app.models
        if not models:
            self.logger.warning('Cms extensions requires models extension')
        else:
            yield api.Crud('pages', models.page,
                           form_class=PageForm,
                           content_manager=PageContentManager())
            yield api.Crud(CONTENT_API_URL, models.content)
