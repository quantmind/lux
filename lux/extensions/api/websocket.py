import json
import time

from pulsar import PermissionDenied, BadRequest
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
        * ``data`` dictionary/list of instance fields
        '''
        try:
            message = json.loads(message)
            action = message.get('action', '').lower().replace('-', '_')
            handle = getattr(self, action, None) if action else None
            if not handle:
                if action:
                    raise BadRequest('Unknown "%s" action' % message['action'])
                else:
                    raise BadRequest('Message action not available')
            else:
                yield from handle(websocket, message)
        except Exception as e:
            status = getattr(e, 'status', 500)
            msg = str(e) or e.__class__.__name__
            self.error(websocket, message, msg, status)

    ########################################################################
    ##    HANDLERS
    def get(self, websocket, message):
        '''Handle get response.

        the ``data`` entry can be a dictionary with the primary key used to
        retrieve the instance, or a list.
        '''
        manager = self.manager(websocket, message)
        pks = message.get('data')
        pkname = manager._meta.pkname()
        if isinstance(pks, list):
            query = manager.filter(**{pkname: pks})
            instances = yield query.all()
            self.write_instances(websocket, message, instances)
        elif isinstance(pks, dict):
            instance = yield manager.get(**{pkname: pks[pkname]})
            self.write_instance(websocket, message, instance)
        else:
            raise BadRequest('Cannot get instance')

    def post(self, websocket, message):
        '''Create a new model.
        '''
        manager = self.manager(websocket, message)
        create = self.update_create
        if websocket.handshake.has_permission('create', manager):
            data = message.get('data')
            if data is not None:
                instance = yield create(websocket, manager, data)
                self.write_instance(websocket, message, instance, 201)
            else:
                raise BadRequest('Cannot create model. No data')
        else:
            raise PermissionDenied

    def put(self, websocket, message):
        '''Update a model.
        '''
        manager = self.manager(websocket, message)
        data = message.get('data')
        if data:
            update = self.update_create
            pkname = manager._meta.pkname()
            pk = data.get(pkname)
            if pk:
                instance = yield manager.get(**{pkname: pk})
                if websocket.handshake.has_permission('update', instance):
                    instance = yield update(websocket, manager, data, instance)
                    self.write_instance(websocket, message, instance)
                else:
                    raise PermissionDenied
            else:
                raise BadRequest('Cannot Update model. No primary key in data')
        else:
            raise BadRequest('Cannot Update model. No data.')

    def delete(self, websocket, message):
        '''Handle get response. Requires a model.'''
        manager = self.manager(websocket, message)
        data = message.get('data')
        if data:
            pkname = manager._meta.pkname()
            pk = data.get(pkname)
            if pk:
                instance = yield manager.get(pk)
                if websocket.handshake.has_permission('delete', instance):
                    yield instance.delete()
                    self.write(websocket, message, 204)
                else:
                    raise PermissionDenied
            else:
                raise BadRequest('Cannot delete. No primary key in data')
        else:
            raise BadRequest('Cannot delete. Missing data in message')

    def status(self, websocket, message):
        started = websocket.handshake.cache.started
        if not started:
            websocket.handshake.cache.started = started = time.time()
        message['data'] = {'uptime': time.time() - started}
        self.write(websocket, message)

    ########################################################################
    ##    INTERNALS
    def write(self, websocket, message, status=200):
        message['status'] = status
        websocket.write(json.dumps(message))

    def manager(self, websocket, message):
        '''Get the manager for a :ref:`CRUD message <crud-message>`.'''
        model = message.get('model')
        if not model:
            raise BadRequest('Model type not available')
        else:
            manager = getattr(websocket.handshake.models, model, None)
            if not manager:
                raise BadRequest('Unknown model %s' % model)
            else:
                return manager

    def update_create(self, websocket, manager, fields, instance=None):
        '''Internal method invoked by both the :meth:`post` and and
        :meth:`put` methods, respectively when creating and updating
        an ``instance`` of a model.

        :parameter websocket: the websocket serving the request.
        :parameter manager: the model manager.
        :parameter fields: model fields used to create or update the
            ``instance``.
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
        self.write(websocket, {'mid': mid, 'data': data})

    def write_instance(self, websocket, message, instance, status=200):
        message['data'] = instance.tojson()
        self.write(websocket, message, status)

    def error(self, websocket, message, msg, status=500):
        '''Handle an error in response'''
        if status == 500:
            websocket.handshake.app.logger.exception(msg)
        else:
            websocket.handshake.app.logger.warning(msg)
        if not isinstance(message, dict):
            message = {}
        message['error'] = msg
        message.pop('data', None)
        self.write(websocket, message, status)
