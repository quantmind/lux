

class Transport:
    name = ''

    @property
    def cache(self):
        return self.handshake.cache

    @property
    def config(self):
        return self.handshake.config

    @property
    def app(self):
        return self.handshake.app

    def on_open(self, client):
        raise NotImplementedError
