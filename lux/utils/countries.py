"""
List of countries
"""
from datetime import datetime

import pytz

# from geoip import geolite2


_better_names = {'GB': 'United Kingdom'}


def better_country_names():
    names = dict(((key, _better_names.get(key, value))
                  for key, value in pytz.country_names.items()))
    return sorted(names.items(), key=lambda d: d[1])


def countries_lookup():
    return sorted(better_country_names(), key=lambda t: t[1])


def _timezones():
    """Yield timezone name, gap to UTC and UTC
    """
    for item in pytz.common_timezones:
        dt = datetime.now(pytz.timezone(item)).strftime('%z')
        utc = '(UTC%s:%s)' % (dt[:-2], dt[-2:])
        gap = int(dt)
        yield item, gap, utc


def _common_timezones():
    for item, g, utc in sorted(_timezones(), key=lambda t: t[1]):
        yield item, utc


common_timezones = [(item, '%s  -  %s' % (utc, item))
                    for item, utc in _common_timezones()]

country_names = tuple(better_country_names())


def timezone_info(request, data):
    return data
