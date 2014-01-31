'''
Interface to Akismet

http://akismet.com/
'''
import lux


class Extension(lux.Extension):
    _config = [
        Parameter('AKISMET_API_KEY', None, 'Askimet API Key')
    ]
