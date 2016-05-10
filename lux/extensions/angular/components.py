import json

from pulsar.apps.wsgi import Html


def grid(options):
    return Html('lux-grid').attr('grid-options', json.dumps(options)).render()
