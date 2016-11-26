import os
from itertools import chain
from urllib.parse import urlparse
from asyncio import gather

from pulsar.apps.test.wsgi import HttpTestClient

from lux.core import LuxCommand, Setting, CommandError


class Command(LuxCommand):
    option_list = (
        Setting('base_url',
                ['--base-url'],
                nargs=1,
                desc='Static website base url'),
        Setting('static_path',
                ['--static-path'],
                desc='Path where to install files'),)

    help = "create a static site"

    async def run(self, options):
        try:
            from bs4 import BeautifulSoup as bs
        except ImportError:
            raise CommandError(
                'Requires BeautifulSoup: pip install beautifulsoup4'
            ) from None

        path = options.static_path
        if not path:
            path = os.getcwd()
        base = options.base_url[0]
        self.bs = bs
        self.http = HttpTestClient(self.app.callable, wsgi=self.app)
        self.files = {}
        await self.build_from_rurls(path, base, ['%s/sitemap.xml' % base])

    async def build_from_rurls(self, path, base, urls):
        await gather(*[self.build(path, base, url) for url in urls])

    async def build(self, path, base, url):
        if url in self.files:
            self.app.logger.warning('Url %s already processed', url)
            return
        self.files[url] = None
        response = await self.http.get(url)
        response.raise_for_status()
        urlp = urlparse(url)
        #
        # save file
        html = response.text()
        rel_path = urlp.path
        if not rel_path:
            rel_path = 'index'

        if url.endswith('.xml'):
            soup = self.bs(response.content, 'html.parser')
            urls = []
            for u in chain(soup.findAll('sitemap'), soup.findAll('url')):
                loc = u.find('loc')
                if not loc:
                    continue
                url = loc.string
                if url.startswith(base):
                    urls.append(url)
            if urls:
                await self.build_from_rurls(path, base, urls)
        else:
            rel_path = '%s.html' % rel_path

        bits = [r for r in rel_path.split('/') if r]
        filename = os.path.join(path, *bits)
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        with open(filename, 'w') as fp:
            fp.write(html)
        self.files[url] = filename
