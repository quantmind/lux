from urllib.parse import urlsplit

from pulsar.utils.httpurl import is_absolute_uri


def is_url(url):
    p = urlsplit(url)
    return p.scheme and p.netloc


def iso8601(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def absolute_uri(request, url):
    if url and not is_absolute_uri(url):
        return request.absolute_uri(url)
    return url
