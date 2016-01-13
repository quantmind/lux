import os
import shutil
import json

from .static import dst_path


suffixes = frozenset(('fjson', 'json', 'txt', 'inv'))


def skip_file(filename):
    bits = filename.split('.')
    if len(bits) == 1:
        return True
    suffix = bits[-1]
    if suffix not in suffixes:
        return True
    return False


def build_content(src, app):
    location = app.config['STATIC_LOCATION']
    for dirpath, _, filenames in os.walk(src):
        for filename in filenames:
            if skip_file(filename):
                continue
            full_src = os.path.join(dirpath, filename)
            if filename.endswith('.fjson'):
                build_page(app, dirpath, filename, src, location)
            else:
                full_dst = dst_path(dirpath, filename, src, location)
                shutil.copyfile(full_src, full_dst)


def build_page(app, dirpath, filename, src, location):
    bits = filename.split('.')
    bits[-1] = 'html'
    full_src = os.path.join(dirpath, filename)
    dst_path(dirpath, '.'.join(bits), src, location)

    with open(full_src, 'r') as fp:
        json.loads(fp.read())
