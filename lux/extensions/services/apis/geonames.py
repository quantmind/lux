import json

from lux import Parameter
from lux.extensions.services import API, api_function, OAuth2


def as_list(f):
    def _(*args, **kwargs):
        return list(f(*args, **kwargs))
    return _


def safe_get(info, name, converter=None):
    v = info.get(name, None)
    try:
        return converter(v)
    except:
        return v


@as_list
def country_info(api, result):
    for info in result.get('geonames', []):
        info['name'] = safe_get(info, 'countryName')
        info['ccy'] = safe_get(info, 'currencyCode')
        info['population'] = safe_get(info, 'population', int)
        info['areaInSqKm'] = safe_get(info, 'areaInSqKm', float)
        yield info


class Geonames(API):
    BASE_URL = 'http://api.geonames.org'
    #auth_class = auth.KeyAuth
    json = True
    params = [Parameter('GEONAMES_USERNAME', None, 'Geonames username')]

    def setup(self, username=None, **params):
        self.username = username

    @classmethod
    def build(cls, cfg=None):
        if cfg:
            un = cfg.get('GEONAMES_USERNAME')
            if un:
                return cls(username=un)

    country_info = api_function('/countryInfoJSON',
                                allowed_params={'style': 'full',
                                                'formatted': 'true'},
                                callback=country_info)
