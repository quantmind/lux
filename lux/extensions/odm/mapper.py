from collections import OrderedDict

from sqlalchemy.event import listens_for

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
        models = OrderedDict()
        for module in self.app.module_iterator('models'):
            models.update(odm.get_models(module) or ())
            models.update(((table.key, table) for table
                           in odm.module_tables(module)))
        for model in models.values():
            self.register(model)
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

    def __init__(self, mapper, request=None, **options):
        super().__init__(mapper, **options)
        self.request = request

    @property
    def app(self):
        return self.mapper.app

    def changes(self):
        for targets, operation in ((self.new, 'create'),
                                   (self.dirty, 'update'),
                                   (self.deleted, 'delete')):
            for target in targets:
                yield target, operation


@listens_for(LuxSession, 'before_flush')
def before_flush(session, flush_context=None, instances=None):
    session.app.fire('on_before_flush', session, safe=True)


@listens_for(LuxSession, 'after_flush')
def after_flush(session, flush_context=None, instances=None):
    session.app.fire('on_after_flush', session, safe=True)


@listens_for(LuxSession, 'before_commit')
def before_commit(session, flush_context=None, instances=None):
    session.app.fire('on_before_commit', session, safe=True)


@listens_for(LuxSession, 'after_commit')
def after_commit(session, flush_context=None, instances=None):
    session.app.fire('on_after_commit', session, safe=True)


@listens_for(LuxSession, 'after_rollback')
def after_rollback(session, flush_context=None, instances=None):
    session.app.fire('on_after_rollback', session, safe=True)
