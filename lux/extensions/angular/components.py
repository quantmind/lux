import json

from pulsar.apps.wsgi import Html


def grid(options):
    return Html('lux-grid').attr('grid', json.dumps(options)).render()
