import os

from pulsar.utils.html import slugify

from lux import Html, Template

from .contents import Snippet
from .builder import Content, BuildError


class BlogSnippet(Snippet):

    def html_main(self, request):
        content = self._content
        meta = self._metadata
        title = meta.get('title')
        if title:
            app = request.app
            title = '<h1>%s</h1>' % self.title
            if self.date:
                title += '<p>%s</p>' % app.format_date(self.date)
            content = '%s\n%s' % (title, content)
        return content


class Blog(Content):
    '''A specialised :class:`~lux.extensions.static.builder.Content`
    to create a blog roll from a directory.

    :param archive=True: if ``True`` blog posts are organised in folders
        by year and month of publication. The url of a blog post
        is given by ``<year>/<month>/<slug>``. Alternatively, the url
        is given by the ``<slug>`` only.
    :param drafts='drafts': url for drafts. If ``None``, drafts are not
        compiled.
    '''
    def __init__(self, path=None, archive=True, drafts='drafts', snippet=None,
                 **context):
        self.archive = archive
        self.drafts = drafts
        snippet = snippet or BlogSnippet
        super().__init__(path=path, snippet=snippet, **context)

    def _build(self, path, app, name, location, context):
        c = self._children
        drafts = []
        years = {}
        all = {}
        #
        if os.path.isdir(path):
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                    src = os.path.join(dirpath, filename)
                    try:
                        entry = yield from c.build_content(app, src)
                    except BuildError as e:
                        app.logger.warning(str(e))
                        continue
                    dt = entry.date
                    title = entry.title
                    if not dt:
                        app.logger.warning('Cannot build post "%s" in "%s" '
                                           'no date', src, name)
                    elif not title:
                        app.logger.warning('Cannot build blog post "%s" '
                                           'no title', src)
                    else:
                        slug = entry._metadata.get('slug')
                        if not slug:
                            slug = slugify(title)
                        entry._metadata['slug'] = slug = slug.lower()

                        if entry.draft:
                            drafts.append(entry)
                        else:
                            if not self.archive:
                                if slug in all:
                                    app.logger.exception('Cannot build '
                                                     '"%s" already available')
                                    continue
                                else:
                                    all[slug] = entry
                            year = years.get(dt.year)
                            if not year:
                                years[dt.year] = year = {}
                            month = year.get(dt.month)
                            if not month:
                                year[dt.month] = month = {}
                            if slug in month:
                                app.logger.exception('Cannot build '
                                                     '"%s" already available')
                            else:
                                month[slug] = entry
            posts = []
            for year in reversed(sorted(years)):
                months = years[year]
                for month in reversed(sorted(months)):
                    month = months[month]
                    for entry in reversed(sorted((m for m in month.values()),
                                                 key=lambda e: e.date)):
                        dt = entry.date
                        if self.archive:
                            path = os.path.join(name, str(year),
                                                dt.strftime('%m'),
                                                entry._metadata['slug'])
                        else:
                            path = os.path.join(name, entry._metadata['slug'])
                        yield from c.build_file(app, entry, path, location,
                                                context)
                        posts.append((entry, path))
            # Create the blog index
            index = self.blog_index(app, posts)
            dst = os.path.join(name, 'index')
            yield from self.build_file(app, index, dst, location, context)
            #
            # Create drafts page
            if self.drafts:
                meta = {'robots': 'noindex, nofollow'}
                posts = []
                name = os.path.join(name, self.drafts)
                for entry in sorted(drafts, key=lambda x: x.date):
                    slug = entry._metadata['slug']
                    path = os.path.join(name, slug)
                    yield from c.build_file(app, entry, path, location,
                                            context, meta=meta)
                    posts.append((entry, path))
                index = self.blog_index(app, posts, True)
                dst = os.path.join(name, 'index')
                yield from self.build_file(app, index, dst, location,
                                           context, meta=meta)
        else:
            raise ValueError('Blog content requires a directory of blog posts')

    def blog_index(self, app, posts, drafts=False):
        date_format = app.config['DATE_FORMAT']
        container = Html('div')
        metadata = None
        if drafts:
            container.append(Html('h1', 'Blog drafts'))
            if not posts:
                container.append(Html('p', 'Nothing here!'))
        elif not posts:
            container.append(Html('div', '<p>No posts yet! Coming soon</p>',
                                  cn="jumbotron"))
        for entry, path in posts:
            path = '/%s' % path
            date = entry.date
            meta = entry._metadata
            elem = Html('div',
                        Html('h4', Html('a', entry.title, href=path)),
                        Html('p', date.strftime(date_format), cn='text-muted'),
                        cn='blog-entry')
            if 'summary-html' in meta:
                elem.append(Html('p', meta['summary-html']))
            container.append(elem)
        return self._snippet(container.render())
