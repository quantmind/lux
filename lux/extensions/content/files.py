import os

from lux.utils.files import skipfile, get_rel_dir

from lux.core import cached
from .contents import get_reader


def content_location(app, *args):
    repo = app.config['CONTENT_REPO']
    if repo:
        location = app.config['CONTENT_LOCATION']
        if location:
            repo = os.path.join(repo, location)
        if args:
            repo = os.path.join(repo, *args)
    return repo


@cached
def get_context_files(app):
    '''Load static context
    '''
    ctx = {}
    location = content_location(app, 'context')
    if location and os.path.isdir(location):
        for dirpath, dirs, filenames in os.walk(location, topdown=False):
            if skipfile(os.path.basename(dirpath) or dirpath):
                continue
            for filename in filenames:
                if skipfile(filename):
                    continue
                file_bits = filename.split('.')
                bits = [file_bits[0]]

                prefix = get_rel_dir(dirpath, location)
                while prefix:
                    prefix, tail = os.path.split(prefix)
                    bits.append(tail)

                filename = os.path.join(dirpath, filename)
                suffix = get_reader(app, filename).suffix
                name = '_'.join(reversed(bits))
                if suffix:
                    name = '%s_%s' % (suffix, name)
                ctx[name] = filename
    return ctx
