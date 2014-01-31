from pulsar.apps.ws import WS
import lux


class ServerInfo(WS):

    def on_open(self):
        pass


class Server(lux.Extension):
    '''Provide middleware to display pulsar server information'''
    route = '/server'

    def __middleware__(self):
        ServerInfo('/stream')
