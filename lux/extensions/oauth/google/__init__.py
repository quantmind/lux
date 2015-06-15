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

from ..oauth import OAuth2, register_oauth


@register_oauth
class Google(OAuth2):
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://accounts.google.com/o/oauth2/token"
    default_scope = ['profile', 'email']

    def on_html_document(self, request, doc):
        self.google_context(doc)
        self.add_analytics(doc)
        key = self.config.get('simple_key')
        if key:
            sensor = 'true' if self.config.get('map_sensor') else 'false'
            url = google_map_url % (key, sensor)
            doc.head.scripts.paths['google-maps'] = {'url': url}
            doc.head.embedded_js.append(run_google_maps_callbacks)

    def google_context(self, doc):
        ngmodules = set(doc.jscontext.get('ngModules', ()))
        ngmodules.add('lux.google')
        doc.jscontext['ngModules'] = list(ngmodules)
        google = doc.jscontext.get('google')
        if google is None:
            doc.jscontext['google'] = {}

    def add_analytics(self, doc):
        google = doc.jscontext['google']
        analytics = self.config.get('analytics')
        if analytics and 'id' in analytics:
            google['analytics'] = analytics
            if 'ga' not in analytics:
                analytics['ga'] = 'ga'
            txt = GOOGLE_ANALYTICS.substitute(analytics)
            doc.head.append(txt)


GOOGLE_ANALYTICS = Template('''\
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','$ga');

  $ga('create', '$id', 'auto');
  $ga('send', 'pageview');

</script>''')


run_google_maps_callbacks = '''
var google_maps_callbacks = [],
    google_maps_loaded = false,
    run_google_maps_callbacks = function () {
        while (google_maps_callbacks.length) {
            var callbacks = google_maps_callbacks;
            google_maps_callbacks = [];
            for (var i=0;i<callbacks.length;i++) {
                callbacks[i]();
            }
        }
        google_maps_loaded = true;
    },
    on_google_map_loaded = function (callback) {
        if (google_maps_loaded) callback()
        else google_maps_callbacks.push(callback);
    };
'''


google_map_url = ('https://maps.googleapis.com/maps/api/js?'
                  'key=%s&sensor=%s&'
                  'callback=run_google_maps_callbacks')
