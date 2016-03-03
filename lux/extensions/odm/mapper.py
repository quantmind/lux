import odm

from pulsar import ImproperlyConfigured

__all__ = ['Mapper', 'model_base']


model_base = odm.model_base


class Mapper(odm.Mapper):
    '''SQLAlchemy wrapper for lux applications
    '''

    def __init__(self, app, binds):
        self.app = app
        super().__init__(binds)
        for module in self.app.module_iterator('models'):
            self.register_module(module)
        if self.is_green and not app.config['GREEN_POOL']:
            raise ImproperlyConfigured('ODM requires a greenlet pool but '
                                       'GREEN_POOL is not set to a positive '
                                       'integer.')

    def copy(self, binds):
        return self.__class__(self.app, binds)

    def session(self, **options):
        options['binds'] = self.binds
        return LuxSession(self, **options)


class LuxSession(odm.OdmSession):

    @property
    def app(self):
        return self.mapper.app

    @classmethod
    def signal(cls, session, changes, event):
        '''Signal changes on session
        '''
        session.app.fire(event, session, changes)
