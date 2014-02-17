import json
import time

from pulsar import HttpException
from pulsar.apps import ws


__all__ = ['CrudWebSocket']


class CrudWebSocket(ws.WS):
    '''A websocket handler for CRUD operations
    '''
    def on_open(self, websocket):
        websocket.handshake.cache.started = time.time()

    def on_message(self, websocket, message):
        '''Handle an incoming text message which is JSON encoded.

        The decoded message is a dictionary containing the following entries:

        * ``action``, the action to perform on the data included in
          the message.
          The action must be implemented as a method of this class.
          Available out of the box are the CRUD actions :meth:`get`,
          :meth:`post`, :meth:`put` and :meth:`delete`.
        * ``mid``, the message unique identifier.
        '''
        message = json.loads(message)
        mid = message.get('mid')
        action = message.get('action', '').lower().replace('-', '_')
        handle = getattr(self, action, None) if action else None
        if not handle:
            if action:
                self.error(websocket, message, 'Unknown "%s" action.'
                           % message['action'])
            else:
                self.error(websocket, message, 'Message action not available')
        else:
            return handle(websocket, message)

    ########################################################################
    ##    HANDLERS
    def get(self, websocket, message):
        '''Handle get response. Requires a model.'''
        manager = self.manager(websocket, message)
        if manager:
            pks = message.get('data')
            if pks:
                query = manager.filter(**{manager._meta.pkname(): pks})
                instances = yield query.all()
                self.write_instances(websocket, message, instances)

    def post(self, websocket, message):
        '''Handle post response for a bulk update/creation of models.

        Requires a model.
        '''
        manager = self.manager(websocket, message)
        if manager:
            create = self.update_create
            if websocket.handshake.has_permission('create', manager):
                data_list = message.get('data')
                saved = []
                for data in data_list:
                    cid = data.get('id')
                    instance = yield create(websocket, manager, data['fields'])
                    if cid:
                        instance._cid = cid
                    saved.append(instance)
                self.write_instances(websocket, message, saved)
            else:
                self.error(websocket, message, 'Permission denied')

    def put(self, websocket, message):
        '''Handle put response.

        Requires a the ``data`` key in ``message`` to be
        a list of dictionaries containg ``pk`` and ``fields`` to update.
        '''
        manager = self.manager(websocket, message)
        if manager:
            update = self.update_create
            pkname = manager._meta.pkname()
            data = message['data']
            pks = dict(((str(d['pk']), d) for d in data if 'pk' in d))
            saved = []
            if pks:
                instances = yield manager.filter(**{pkname: tuple(pks)}).all()
                for instance in instances:
                    if websocket.handshake.has_permission('update', instance):
                        pk = str(instance.pkvalue())
                        item = pks[pk]
                        instance = yield update(websocket, manager,
                                                item.get('fields'),
                                                instance)
                        instance._cid = item.get('cid')
                        saved.append(instance)
            self.write_instances(websocket, message, saved)

    def delete(self, websocket, message):
        '''Handle get response. Requires a model.'''
        manager = self.manager(websocket, message)
        if manager:
            pass

    def status(self, websocket, message):
        started = websocket.handshake.cache.started
        if not started:
            websocket.handshake.cache.started = started = time.time()
        message['data'] = {'uptime': time.time() - started}
        self.write(websocket, message)

    ########################################################################
    ##    INTERNALS
    def write(self, websocket, message):
        websocket.write(json.dumps(message))

    def manager(self, websocket, message):
        '''Get the manager for a :ref:`CRUD message <crud-message>`.'''
        model = message.get('model')
        if not model:
            self.error(websocket, message, 'Model type not available')
        else:
            manager = getattr(websocket.handshake.models, model, None)
            if not manager:
                self.error(websocket, message, 'Unknown model %s' % model)
            else:
                return manager

    def update_create(self, websocket, manager, fields, instance=None):
        '''Internal method invoked by both the :meth:`post` and and :meth:`put`
method, respectively when creating and updating an ``instance`` of a model.

:parameter websocket: the websocket serving the request.
:parameter manager: the model manager.
:parameter fields: model fields used to create or update the ``instance``.
:parameter instance: Optional instance of the ``manager`` model
    (when updating).
:return: a new or an updated ``instance``
'''
        if instance is None:
            return manager.new(**fields)
        else:
            for name in fields:
                instance.set(name, fields[name])
            return manager.save(instance)

    def write_instances(self, websocket, message, instances):
        data = []
        if instances:
            for i in instances:
                pk = i.pkvalue()
                data.append({'fields': i.tojson(),
                             'pk': pk,
                             'cid': getattr(i, '_cid', pk)})
        message['data'] = data
        self.write(websocket, message)

    def error(self, websocket, message, msg):
        '''Handle an error in response'''
        websocket.handshake.app.logger.warning(msg)
        message['error'] = msg
        message.pop('data', None)
        self.write(websocket, message)
