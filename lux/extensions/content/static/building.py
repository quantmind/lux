import os

from lux.utils.files import skipfile, get_rel_dir
from lux import BuildError


def split(filename):
    bits = filename.split('.')
    ext = None
    if len(bits) > 1:
        ext = bits[-1]
        filename = '.'.join(bits[:-1])
    return filename, ext


def all_files(app, router, src):
    '''Generator of all files within a directory
    '''
    if os.path.isdir(src):
        for dirpath, _, filenames in os.walk(src):
            if skipfile(os.path.basename(dirpath) or dirpath):
                continue
            rel_dir = get_rel_dir(dirpath, src)
            for filename in filenames:
                if skipfile(filename):
                    continue
                name, ext = split(filename)
                name = os.path.join(rel_dir, name)
                fpath = os.path.join(dirpath, filename)
                yield name, fpath, ext
    #
    elif os.path.isfile(src):
        dirpath, filename = os.path.split(src)
        assert not filename.startswith('.')
        name, ext = split(filename)
        fpath = os.path.join(dirpath, filename)
        yield name, dirpath, ext
    #
    else:
        raise BuildError("'%s' not found." % src)
