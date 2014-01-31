module('lux.web.backends');


var BackendTest = lux.Class.extend({
    //
    init: function (Todo, backend, expect, timeout) {
        this.Todo = Todo;
        this.expect = expect || 27;
        this.timeout = timeout || 5;
        this.failure = false;
        this.backend = backend;
    },
    //
    check: function () {
        var self = this;
        if (_.size(this.backend._pending_messages) && !this.failure) {
            lux.eventloop.call_later(0.1, function () {
                self.check();
            });
        } else {
            if (this.timeout) {
                this.timeout.cancel();
            } else {
                ok(false, 'Timeout occurred');
            }
            start();
        }
    },
    //
    start: function () {
        var self = this,
            backend = this.backend,
            Todo = this.Todo;
        //
        // Try to ping
        backend.send({
            action: 'ping',
            success: function (data, b, response) {
                equal(data, 'pong', 'websocket ping got pong');
                equal(b, backend);
                equal(response.data, data);
                equal(response.action, 'ping');
            }
        });
        //
        backend.send({
            action: 'pippo',
            error: function (error, b, response) {
                equal(error, 'Unknown "pippo" action.',  'Unknown "pippo" action.');
                equal(error, response.error);
                equal(response.action, 'pippo');
            }
        });
        //
        Todo._meta.set_transport(backend);
        equal(Todo._meta._backend, backend);
        //
        var todo = new Todo({title: 'write more tests'});
        ok(todo.isNew(), 'instance ' + todo + ' is new');
        ok(!todo.pk(), '... and has no primary key');
        ok(todo.id(), '... and its id is ' + todo.id());
        equal(todo, todo._meta.live(todo.id()), '... and it is in live instances');
        equal(todo.get('title'), 'write more tests', '... and has valid field');
        equal(_.size(todo.fields()), 1, '... and has only one field');
        equal(todo.fields().title, todo.get('title'));
        //
        // now sync the model
        todo.sync({
            success: function (data) {
                // Got a succesful response from the server
                ok(!todo.isNew(), 'Model ' + todo + ' is persistent');
                equal(todo.get('id'), todo.pk(), '... id and pk are the same: ' + todo.pk());
                self.test_update(todo);
            }
        });
        //
        this.check();
    },
    //
    test_update: function (todo) {
        equal(_.size(todo.changedFields()), 0, '... it has 0 changes');
        var self = this,
            d = new Date(2020,1,1),
            v = d.getTime();
        todo.set('when', d);
        var changed = todo.changedFields();
        equal(_.size(changed), 1, '... now it has 1 change');
        // Now we synch changes
        todo.sync({
            success: function (data) {
                equal(todo.get('when').getTime(), v, ' ... it has the right date after update');
                self.test_get(todo.pk());
            }
        });
    },
    //
    test_get: function (id) {
        // First clear the current cache
        var Todo = this.Todo,
            live = Todo._meta.live();
        equal(live.length, 1, 'There is 1 value in the live elements');
        var todo2 = new Todo();
        live = Todo._meta.live();
        equal(live.length, 2, 'There are 2 values in the live elements');
        Todo._meta.clear();
        live = Todo._meta.live();
        equal(live.length, 0, 'There are 0 values in the live elements');
        //
        // Get the value
        Todo._meta.get(id, {
            success: function (data, b, result) {
                equal(data.length, 1, 'One instance fetched');
                var t = data[0];
                equal(t.id(), id, 'Same id');
                equal(_.size(t.fields()), 3, 'It has three fields');
            }
        });
    }
});


var all = {
        local: BackendTest.extend({
            init: function () {
                var backend = new lux.Storage({type: 'session'});
                this._super(Todo1, backend);
            },
            start: function () {
                equal(this.backend.options.type, 'session', 'Local storage is session based');
                this._super();
            }
        }),
        websocket: BackendTest.extend({
            init: function () {
                this._super(Todo2);
            },
            start: function (backend) {
                if (!backend) {
                    var self = this,
                        b = new lux.Socket('socket', {
                                reconnecting: 0,
                                onopen: function () {
                                    self.start(this);
                                }
                            });
                } else {
                    this.backend = backend;
                    equal(backend.options.reconnecting, 0, 'Reconnecting is 0');
                    this._super();
                }
            }
        })
    };

_(all).forEach(function (Backend, name) {
    var test = new Backend();
    asyncTest(name + " backend", test.expect, function () {
        //
        // Set the timeout for the test
        test.timeout = lux.eventloop.call_later(test.timeout, function () {
            test.timeout = null;
            test.failure = true;
        });
        //
        test.start();
    });
});
