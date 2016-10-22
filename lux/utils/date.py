import time
from datetime import date, datetime, timedelta

from dateutil.parser import parse as dateparser

import pytz


NUMBER = (int, float)
dayfmt = "%04d-%02d-%02d%c"
seconds = '{:02d}:{:02d}:{:02d}'


def iso8601(dt, sep='T'):
    s = (dayfmt % (dt.year, dt.month, dt.day, sep) +
         seconds.format(dt.hour, dt.minute, dt.second))

    off = dt.utcoffset()
    if off is not None:
        if off.days < 0:
            sign = "-"
            off = -off
        else:
            sign = "+"
        hh, mm = divmod(off, timedelta(hours=1))
        mm, ss = divmod(mm, timedelta(minutes=1))
        s += "%s%02d:%02d" % (sign, hh, mm)
        if ss:
            assert not ss.microseconds
            s += ":%02d" % ss.seconds
    return s


def to_timestamp(dt):
    if isinstance(dt, str):
        dt = dateparser(dt)
    if isinstance(dt, date):
        return time.mktime(dt.timetuple())
    elif isinstance(dt, NUMBER):
        return dt
    elif dt is not None:
        raise ValueError(dt)


def date_from_now(seconds):
    return tzinfo(datetime.utcnow() + timedelta(seconds=seconds))


def tzinfo(dt):
    if isinstance(dt, datetime) and not dt.tzinfo:
        dt = pytz.utc.localize(dt)
    return dt
