from string import Template
from urllib.parse import urlparse

import lux
from lux import Parameter


class Extension(lux.Extension):

    _config = [
        Parameter('GOOGLE_ANALYTICS_ID', None,
                  'Google analtics ID')]


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


GOOGLE_ANALYTICS = Template('''\
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', '$id', '$domain');
  ga('send', 'pageview');

</script>''')
