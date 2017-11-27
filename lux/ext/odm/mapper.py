from collections import OrderedDict

from sqlalchemy.event import listens_for

from odm import mapper

from pulsar.api import ImproperlyConfigured

from lux import models

__all__ = ['Mapper', 'model_base']


model_base = mapper.model_base


class Mapper(mapper.Mapper):
    '''SQLAlchemy wrapper for lux applications
    '''

    def __init__(self, app, binds):
        self.app = app
        super().__init__(binds)
        models = OrderedDict()
        for module in self.app.module_iterator('models'):
            models.update(mapper.get_models(module) or ())
            models.update(((table.key, table) for table
                           in mapper.module_tables(module)))
        for model in models.values():
            self.register(model)
        if self.is_green and not app.config['GREEN_POOL']:
            raise ImproperlyConfigured('ODM requires a greenlet pool but '
                                       'GREEN_POOL is not set to a positive '
                                       'integer.')

    def copy(self, binds):
        return self.__class__(self.app, binds)

    def session(self, request=None, **options):
        options['binds'] = self.binds
        return LuxSession(self, request, **options)


class LuxSession(mapper.OdmSession, models.Session):

    def __init__(self, mapper, request=None, **options):
        super().__init__(mapper, **options)
        models.Session.__init__(self, mapper.app, request=request)

    def changes(self):
        for targets, operation in ((self.new, 'create'),
                                   (self.dirty, 'update'),
                                   (self.deleted, 'delete')):
            for target in targets:
                yield target, operation


@listens_for(LuxSession, 'before_flush')
def before_flush(session, flush_context=None, instances=None):
    session.app.fire_event('on_before_flush', data=session)


@listens_for(LuxSession, 'after_flush')
def after_flush(session, flush_context=None, instances=None):
    session.app.fire_event('on_after_flush', data=session)


@listens_for(LuxSession, 'before_commit')
def before_commit(session, flush_context=None, instances=None):
    session.app.fire_event('on_before_commit', data=session)


@listens_for(LuxSession, 'after_commit')
def after_commit(session, flush_context=None, instances=None):
    session.app.fire_event('on_after_commit', data=session)


@listens_for(LuxSession, 'after_rollback')
def after_rollback(session, flush_context=None, instances=None):
    session.app.fire_event('on_after_rollback', data=session)
