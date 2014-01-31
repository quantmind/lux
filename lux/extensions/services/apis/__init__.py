from lux.extensions.services.binder import APIS

from . import github
from . import amazon
from . import google
from . import geonames
from . import dropbox


__all__ = ['available', 'api']


def available(config):
    '''Retrieve a list of API with valid configuration settings'''
    available = []
    for Api in APIS.values():
        a = Api.build(config)
        if a:
            available.append(a)
    return available


def api(name, config=None):
    api = APIS.get(name)
    if api:
        return api.build(config)
