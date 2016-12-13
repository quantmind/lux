'''
Lux comes with a high-level sitemap-generating framework that makes creating
sitemap_ XML files easy.

.. _sitemap: http://www.sitemaps.org/
'''
from urllib.parse import urlencode
from datetime import datetime

from dateutil.parser import parse as parse_date

from pulsar.apps.wsgi import Router
from pulsar.utils.httpurl import urllibr

from lux.core import Parameter, cached, LuxExtension


PING_URL = "http://www.google.com/webmasters/tools/ping"


class Extension(LuxExtension):

    _config = [Parameter('CACHE_SITEMAP_TIMEOUT', None,
                         ('Sitemap cache timeout, if not set it defaults to '
                          'the CACHE_DEFAULT_TIMEOUT parameter'))]


def ping_google(sitemap_url, ping_url=PING_URL):
    """
    Alerts Google that the sitemap at ``sitemap_url`` has been updated.
    """
    params = urlencode({'sitemap': sitemap_url})
    return urllibr.urlopen("%s?%s" % (ping_url, params))


class BaseSitemap(Router):
    # This limit is defined by Google. See the index documentation at
    # http://www.sitemaps.org/protocol.html
    limit = 50000
    tag = None
    item_tag = None
    extra_item_tags = ()
    version = '<?xml version="1.0" encoding="UTF-8"?>'
    xmlns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    response_content_types = ('application/xml', 'text/xml')

    def items(self, request):
        '''Generetors of items to include in the sitemap
        '''
        return ()

    def get(self, request):
        response = request.response
        sitemap, _ = self.sitemap(request)
        response.content = sitemap
        return response

    @cached(timeout='CACHE_SITEMAP_TIMEOUT')
    def sitemap(self, request):
        sitemap = [self.version,
                   '<%s xmlns="%s">' % (self.tag, self.xmlns)]
        sitemap.extend(self._urls(request))
        sitemap.append('</%s>' % self.tag)
        return '\n'.join(sitemap), request.cache.pop('latest_lastmod')

    def _urls(self, request):
        latest_lastmod = None
        all_items_lastmod = True  # track if all items have a lastmod
        count = 0
        for item in self.items(request):
            loc = self._get('loc', item)
            priority = self._get('priority', item)
            # No location or priority set to 0
            if not loc or priority == 0 or priority == '0':
                continue
            count += 1
            if count > self.limit:
                request.error('Maximum number of sitemap entries reached')
                break

            lastmod = self._get('lastmod', item)
            if lastmod:
                if isinstance(lastmod, str):
                    lastmodv = parse_date(lastmod)
                else:
                    lastmodv = lastmod

                if isinstance(lastmodv, datetime):
                    lastmodv = lastmodv.date()
                lastmod = lastmodv.isoformat()

                if (all_items_lastmod and
                        (latest_lastmod is None or lastmodv > latest_lastmod)):
                    latest_lastmod = lastmodv
            else:
                all_items_lastmod = False

            values = [self._xml('loc', loc), self._xml('lastmod', lastmod)]

            for tag in self.extra_item_tags:
                values.append(self._xml(tag, self._get(tag, item)))

            yield self._xml(self.item_tag, ''.join(values))

        if all_items_lastmod and latest_lastmod:
            latest_lastmod = latest_lastmod.isoformat()
        else:
            latest_lastmod = None
        request.cache.latest_lastmod = latest_lastmod

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


class Sitemap(BaseSitemap):
    tag = 'urlset'
    item_tag = 'url'
    extra_item_tags = ('priority', 'changefreq')


class SitemapIndex(BaseSitemap):
    tag = 'sitemapindex'
    item_tag = 'sitemap'
