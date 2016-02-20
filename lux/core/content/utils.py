import os

from lux.utils.files import skipfile, get_rel_dir

from .contents import get_reader


def static_context(app, location, context):
    '''Load static context from ``location``
    '''
    ctx = {}
    if os.path.isdir(location):
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
                content = get_reader(app, filename).content(filename)
                name = '_'.join(reversed(bits))
                if content.suffix:
                    name = '%s_%s' % (content.suffix, name)
                ctx[name] = content.render(app, context)
                context[name] = ctx[name]
    return ctx
