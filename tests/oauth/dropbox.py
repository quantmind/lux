from lux.utils import test


@test.skipUnless(test.get_params('DROPBOX_CLIENT_ID',
                                 'DROPBOX_CLIENT_SECRET'),
                 'DROPBOX_* required in config.py file.')
class TestDropbox(test.TestCase):
    auth = None
