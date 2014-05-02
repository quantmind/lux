'''
Facilitate google integration

Google API Key
=====================

If the :setting:`GOOGLE_API_KEY` parameter is set to a valid
`google api key`_, this extension allows to interact with several
google services.

Google maps
~~~~~~~~~~~~~~~~~
To use `google maps`_ api, you can require it via the
:meth:`~pulsar.apps.wsgi.content.Scripts.require` method::

    >>> doc.head.scripts.require('google-maps')


Google Analytics
=====================

Set the :setting:`GOOGLE_ANALYTICS_ID` parameter to a valid analytic ID.


.. _`google api key`: http://goo.gl/21m8Vl
.. _`google maps`: goo.gl/21m8Vl
'''
from string import Template
from urllib.parse import urlparse

import lux
from lux import Parameter


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
google_map_url = ('https://maps.googleapis.com/maps/api/js?key=%s&sensor=%s&'
                  'callback=run_google_maps_callbacks')

class Extension(lux.Extension):

    _config = [
        Parameter('GOOGLE_ANALYTICS_ID', None, 'Google analtics ID'),
        Parameter('GOOGLE_API_KEY', None, 'Google API Key'),
        Parameter('GOOGLE_MAP_SENSOR', False, 'Google Map Sensor')]


    def on_html_document(self, app, request, doc):
        id = app.config['GOOGLE_ANALYTICS_ID']
        if id:
            site = app.config['SITE_URL']
            if not site:
                self.logger.warning(
                    'SITE_URL is required for google analytics')
            p = urlparse(site)
            txt = GOOGLE_ANALYTICS.substitute({'id': id, 'domain': p.netloc})
            doc.head.append(txt)
        api_key = app.config['GOOGLE_API_KEY']
        if api_key:
            sensor = 'true' if app.config['GOOGLE_MAP_SENSOR'] else 'false'
            url = google_map_url % (api_key, sensor)
            doc.head.scripts.known_libraries['google-maps'] = url
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
