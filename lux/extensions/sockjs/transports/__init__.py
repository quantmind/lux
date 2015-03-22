

class Transport:
    name = ''

    def on_open(self, client):
        raise NotImplementedError
