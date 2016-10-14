'''\
This module integrates Google OAuth2_ services and APIs with lux.

When the ``google`` dictionary is included into the :setting:`OAUTH_PROVIDERS`
dictionary, the :ref:`google angular module <js-lux-google>` is added to the
:ref:`javascript context object <js-lux-context>` which can be used by
AngularJS if the :mod:`lux.extensions.angular` module is included in
the list of :setting:`EXTENSIONS` of your application.

Google analytics
====================
To use google analytics add the ``analytics`` dictionary to the
``google`` dictionary in :setting:`OAUTH_PROVIDERS`::

    OAUTH_PROVIDERS = {
        ...,
        'google': {
            ...,
            'analytics': {
                'id': 'UA-54439804-2',
                ...
            }
        }
    }

When using google analytics integration with :mod:`lux.extensions.angular`
in `ui.router`_ mode (:setting:`ANGULAR_UI_ROUTER` set to ``True``) one
must be aware that **pageview** events are not triggered anymore.

To handle this situation the :ref:`google angular module <js-lux-google>`
interacts with google analytics to register pageviews and custom events
by listening for the `$stateChangeSuccess` event.

Google maps
===============
To use google map, a ``simple_key`` entry in ``google`` config dictionary must
be specified. The simple key is used by google to identify your project when
you do not need to access user data::

    OAUTH_PROVIDERS = {
        ...,
        'google': {
            'simple_key': '...'
            'map_sensor': True,
            ...
        }
    }

.. _OAuth2: https://developers.google.com/accounts/docs/OAuth2
.. _`ui.router`: http://angular-ui.github.io/ui-router/site
'''
from string import Template

from ..oauth import OAuth2, OAuth2Api


class Api(OAuth2Api):
    url = 'https://www.googleapis.com/adexchangebuyer/v1.3'
    headers = [('content-type', 'application/json'),
               ('x-li-format', 'json')]

    def user(self):
        url = '%s/~' % self.url
        response = self.http.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


class Google(OAuth2):
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://accounts.google.com/o/oauth2/token"
    default_scope = ['profile', 'email']
    fa = 'google'

    def on_html_document(self, request, doc):
        self.add_analytics(request, doc)
        key = self.config.get('simple_key')
        if key:
            sensor = 'true' if self.config.get('map_sensor') else 'false'
            doc.jscontext['googlemaps'] = google_map_url % (key, sensor)

    def add_analytics(self, request, doc):
        id = self.config.get('analytics_id')
        if id:
            rnd = request.app.template_engine()
            txt = rnd(GOOGLE_ANALYTICS, id=id, ga='ga')
            doc.body.before_render(lambda r, b: b.append(txt))


GOOGLE_ANALYTICS = '''\
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','{{ ga }}');

  {{ ga }}('create', '{{ id }}', 'auto');
  {{ ga }}('send', 'pageview');

</script>'''


google_map_url = ('async!https://maps.googleapis.com/maps/api/js?'
                  'key=%s&sensor=%s')
