import time
from datetime import date

from dateutil.parser import parse as dateparser


NUMBER = (int, float)


def iso8601(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def to_timestamp(dt):
    if isinstance(dt, str):
        dt = dateparser(dt)
    if isinstance(dt, date):
        return time.mktime(dt.timetuple())
    elif isinstance(dt, NUMBER):
        return dt
    elif dt is not None:
        raise ValueError(dt)
