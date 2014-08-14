import lux
from lux import Parameter


class Extension(lux.Extension):

    _config = [
        Parameter('DROPBOX_API_KEY', None, 'Dropbox API Key')]
