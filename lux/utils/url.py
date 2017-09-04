from urllib.parse import urlsplit


def is_url(url):
    if url:
        p = urlsplit(url)
        return p.scheme and p.netloc
    return False


def absolute_uri(request, url):
    if not is_url(url):
        return request.absolute_uri(url)
    return url


def initial_slash(path):
    if path and not path.startswith('/'):
        return '/%s' % path
    return path
