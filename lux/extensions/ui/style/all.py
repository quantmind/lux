import os

from importlib import import_module


def add_css(body):
    loaded = set()
    queue = []
    me = os.path.basename(__file__)
    for file in os.listdir(os.path.dirname(__file__)):
        if file.endswith('.py') and file != me and not file.startswith('__'):
            file = file[:-3]
            mod = import_module('lux.extensions.ui.style.%s' % file)
            if try_load(file, mod, loaded, body):
                new_queue = []
                for file, mod in queue:
                    if not try_load(file, mod, loaded, body):
                        new_queue.append((file, mod))
                queue = new_queue
            else:
                queue.append((file, mod))
    assert not queue, "Could not load %s" % ', '.join((t[0] for t in queue))


def try_load(file, mod, loaded, body):
    if hasattr(mod, 'requires'):
        for name in mod.requires:
            if name not in loaded:
                return False
    mod.add_css(body)
    loaded.add(file)
    return True
