from string import Template

from pulsar.utils.httpurl import urlparse

from ..oauth import OAuth2, register_oauth


@register_oauth
class Google(OAuth2):
    '''Googke integration and API

    Additional field to the OAuth2

    * ``analytics_id``    token for google analytics
    * ``simple_key`` to identify your project when you do not need to
      access user data (google map for example)
    * ``map_sensor``
    '''
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://accounts.google.com/o/oauth2/token"
    default_scope = ['profile', 'email']

    def add_meta_tags(self, request, doc):
        aid = self.config.get('analytics_id')
        if aid:
            site = request.config['SITE_URL']
            if not site:
                request.logger.warning(
                    'SITE_URL is required for google analytics')
            p = urlparse(site)
            txt = GOOGLE_ANALYTICS.substitute({'id': aid, 'domain': p.netloc})
            doc.head.append(txt)
        key = self.config.get('simple_key')
        if key:
            sensor = 'true' if self.config.get('map_sensor') else 'false'
            url = google_map_url % (key, sensor)
            doc.head.scripts.known_libraries['google-maps'] = {'url': url,
                                                               'minify': False}
            doc.head.embedded_js.append(run_google_maps_callbacks)


GOOGLE_ANALYTICS = Template('''\
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', '$id', '$domain');
  ga('send', 'pageview');

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


google_map_url = ('https://maps.googleapis.com/maps/api/js?v=3.exp&'
                  'key=%s&sensor=%s&'
                  'callback=run_google_maps_callbacks')
