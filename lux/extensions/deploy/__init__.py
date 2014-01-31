import lux
from lux import Parameter


class Extension(lux.Extension):
    _config = [
        Parameter('SERVER_CONFIGURATION', 'nginx_reverse_proxy', ''),
        Parameter('DOMAIN_NAME', None,
                  'Full domain name of your web site, e.g. '
                  'http://www.example.com')
    ]
