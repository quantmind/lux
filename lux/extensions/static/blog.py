import os

from pulsar.utils.html import slugify

from lux import Html, Template

from .contents import Snippet
from .builder import Content, build_content


class Blog(Content):
    archive = 'archive'
    drafts = 'drafts'

    def _build(self, path, app, name, location, context):
        drafts = []
        years = {}
        if os.path.isdir(path):
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                    src = os.path.join(dirpath, filename)
                    entry = yield from build_content(app, src)
                    dt = entry.date
                    title = entry.title
                    if not dt:
                        app.logger.warning('Cannot build blog post "%s" '
                                           'no date', src)
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
                            year = years.get(dt.year)
                            if not year:
                                years[dt.year] = year = {}
                            month = year.get(dt.month)
                            if not month:
                                year[dt.month] = month = {}
                            if slug in month:
                                app.logger.exception('Cannot build blog post "%s" '
                                                     'already available')
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
                        path = os.path.join(name, str(year), dt.strftime('%m'),
                                            entry._metadata['slug'])
                        yield from self.build_file(app, entry, path, location,
                                                   context)
                        posts.append((entry, path))
            # Create the blog index
            index = self.blog_index(app, posts)
            dst = os.path.join(name, 'index')
            yield from self.build_file(app, index, dst, location, context)
            #
            # Create drafts page
            if self.drafts:
                posts = []
                name = os.path.join(name, self.drafts)
                for entry in sorted(drafts, key=lambda x: x.date):
                    slug = entry._metadata['slug']
                    dst = os.path.join(name, slug)
                    yield from self.build_file(app, entry, dst, location,
                                               context)
                    posts.append((entry, os.path.join(self.drafts, slug)))
                index = self.blog_index(app, posts, drafts=self.drafts)
                dst = os.path.join(name, 'index')
                yield from self.build_file(app, index, dst, location, context)
        else:
            raise ValueError('Blog content requires a directory of blog posts')

    def blog_index(self, app, posts, drafts=None):
        config = app.config
        site_url = config['SITE_URL']
        relative = config['RELATIVE_URLS'] or not site_url
        date_format = config['DATE_FORMAT']
        container = Html('div')
        if drafts:
            container.append(Html('h1', 'Blog drafts'))
            if not relative:
                site_url = '%s/%s' % (site_urls, drafts)
            if not posts:
                container.append(Html('p', 'Nothing here!'))
        elif not posts:
            container.append(Html('div', '<p>No posts yet! Coming soon</p>',
                                  cn="jumbotron"))
        for entry, path in posts:
            if not relative:
                path = '%s/%s' % (site_url, path)
            date = entry.date
            elem = Html('div',
                        Html('h4', Html('a', entry.title, href=path)),
                        Html('p', date.strftime(date_format)),
                        cn='blog-entry')
            container.append(elem)
        return Snippet(container.render())

