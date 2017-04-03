import sys

import pip


def python_packages(request):
    return request.json_response(dict(packages()))


def packages():
    yield 'python', ' '.join(sys.version.split('\n'))
    for p in sorted(_safe_dist(), key=lambda p: p[0]):
        yield p


def _safe_dist():
    for p in pip.get_installed_distributions():
        try:
            yield p.key, p.version
        except Exception:   # pragma    nocover
            pass
