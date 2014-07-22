import os

from pulsar.utils.html import slugify

from lux import Html

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
    def __init__(self, path=None, archive=True, drafts='drafts',
                 snippet=None, **context):
        self.archive = archive
        self.drafts = drafts
        snippet = snippet or BlogSnippet
        super().__init__(path=path, snippet=snippet, **context)

    def _build(self, request, path, name, location, context):
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
                        entry = c.build_content(request, src, context)
                    except BuildError as e:
                        request.logger.error(str(e))
                        continue
                    dt = entry.date
                    if not dt:
                        request.logger.warning('Cannot build post "%s" in '
                                               '"%s" no date', src, name)
                    elif not entry.title:
                        request.logger.warning('Cannot build blog post "%s" '
                                               'no title', src)
                    else:
                        if not entry.slug:
                            entry.slug = slugify(entry.title)
                        entry.slug = entry.slug.lower()

                        if entry.draft:
                            drafts.append(entry)
                        else:
                            if not self.archive:
                                if entry.slug in all:
                                    request.logger.error(
                                        'Cannot build "%s" already available')
                                    continue
                                else:
                                    all[entry.slug] = entry
                            year = years.get(dt.year)
                            if not year:
                                years[dt.year] = year = {}
                            month = year.get(dt.month)
                            if not month:
                                year[dt.month] = month = {}
                            if entry.slug in month:
                                request.logger.error(
                                    'Cannot build "%s" already available')
                            else:
                                month[entry.slug] = entry
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
                                                entry.slug)
                        else:
                            path = os.path.join(name, entry.slug)
                        c.build_file(request, entry, path, location, context)
                        posts.append((entry, path))
            # Create the blog index
            index = self.blog_index(request, posts)
            dst = os.path.join(name, 'index')
            self.build_file(request, index, dst, location, context)
            #
            # Create drafts page
            if self.drafts:
                meta = {'robots': ['noindex', 'nofollow']}
                posts = []
                name = os.path.join(name, self.drafts)
                for entry in sorted(drafts, key=lambda x: x.date):
                    slug = entry.slug
                    path = os.path.join(name, slug)
                    c.build_file(request, entry, path, location,
                                 context, meta=meta)
                    posts.append((entry, path))
                index = self.blog_index(request, posts, True)
                dst = os.path.join(name, 'index')
                self.build_file(request, index, dst, location,
                                context, meta=meta)
        else:
            raise ValueError('Blog content requires a directory of blog posts')

    def blog_index(self, request, posts, drafts=False):
        date_format = request.config['DATE_FORMAT']
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
            elem = Html('div',
                        Html('h4', Html('a', entry.title, href=path)),
                        Html('p', date.strftime(date_format), cn='text-muted'),
                        cn='blog-entry')
            if entry.description:
                elem.append(Html('p', entry.description))
            container.append(elem)
        return self._snippet(container.render())
