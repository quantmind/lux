'''
Lux comes with a high-level sitemap-generating framework that makes creating
sitemap_ XML files easy.

.. _sitemap: http://www.sitemaps.org/
'''
from pulsar.apps.wsgi import Router
from pulsar.utils.httpurl import urllibr, urlencode

import lux


PING_URL = "http://www.google.com/webmasters/tools/ping"


class Extension(lux.Extension):
    '''Dummy extension just to add the ping_google command'''
    pass


def ping_google(sitemap_url, ping_url=PING_URL):
    """
    Alerts Google that the sitemap at ``sitemap_url`` has been updated.
    """
    params = urlencode({'sitemap': sitemap_url})
    return urllibr.urlopen("%s?%s" % (ping_url, params))


class Sitemap(Router):
    # This limit is defined by Google. See the index documentation at
    # http://www.sitemaps.org/protocol.html
    limit = 50000

    response_content_types = ('application/xml', 'text/xml')

    def items(self, request):
        '''Generetors of items to include in the sitemap
        '''
        return ()

    def get(self, request):
        sitemap = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        sitemap.extend(self._urls(request))
        sitemap.append('</urlset>')
        response = request.response
        response.content = '\n'.join(sitemap)
        return response

    def _urls(self, request):
        latest_lastmod = None
        all_items_lastmod = True  # track if all items have a lastmod
        count = 0
        for item in self.items(request):
            loc = self._get('loc', item)
            priority = self._get('priority', item)
            if not loc or priority == 0 or priority == '0':
                continue
            count += 1
            if count > self.limit:
                break
            lastmod = self._get('lastmod', item)
            changefreq = self._get('changefreq', item)
            if lastmod:
                if (all_items_lastmod and
                        (latest_lastmod is None or lastmod > latest_lastmod)):
                    latest_lastmod = lastmod
                lastmod = lastmod.strftime('%Y-%m-%d')
            else:
                all_items_lastmod = False
            yield '<url>%s%s%s%s</url>' % (self._xml('loc', loc),
                                           self._xml('lastmod', lastmod),
                                           self._xml('priority', priority),
                                           self._xml('changefreq', changefreq))

    def _get(self, name, obj):
        try:
            attr = getattr(obj, name)
        except AttributeError:
            return
        if callable(attr):
            attr = attr(obj)
        return attr

    def _xml(self, name, value):
        return '<%s>%s</%s>' % (name, value, name) if value else ''
