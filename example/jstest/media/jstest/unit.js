define(['lux-web', 'qunit'], function () {
    "use strict";
    var web = lux.web,
        test_destroy = function (instance) {
            var elem = instance.element(),
                ext = instance.extension(),
                id = instance.id();
            equal(ext.instance(instance), instance);
            equal(ext.instance(id), instance);
            instance.destroy();
            equal(ext.instance(id), undefined);
        };
    //

    var Todo1 = lux.Model.extend({
        meta: {
            name: 'todo1',
            attributes: {
                'title': null,
                'description': null,
                'when': lux.utils.asDate
            }
        }
    });


    var Todo2 = lux.Model.extend({
        meta: {
            name: 'todo2',
            attributes: {
                'title': null,
                'description': null,
                'when': lux.utils.asDate
            }
        }
    });
module('lux');

test("lux", function() {
    equal(typeof(lux), 'object', 'Lux is an object');
    equal(typeof(lux.utils), 'object', 'lux.utils. is an object');
    //
    equal(typeof(lux.Ordered), 'function', 'Test Ordered collections');
    var o = new lux.Ordered();
    equal(o.size(), 0);
});


test("SkipList", function() {
    var sl = new lux.SkipList();
    equal(sl.length, 0, 'skiplist has 0 length');
    equal(sl.insert(4, 'ciao'), 1);
    equal(sl.insert(2, 'foo'), 2);
    equal(sl.insert(8, 'pippo'), 3);
    equal(sl.length, 3, 'skiplist has 3 elements');
    var r = [];
    sl.forEach(function (value) {
        r.push(value);
    });
    equal(r[0], 'foo', 'Correct first value');
    equal(r[1], 'ciao', 'Correct second value');
    equal(r[2], 'pippo', 'Correct third value');
});
//
//  Test utility functions
//
module('lux.utils');

test("allClasses", function() {
    var allClasses = lux.utils.allClasses,
        el = $('<div>');
    ok(_.isArray(allClasses(el)));
    equal(allClasses(el).length, 0);
    el.addClass('bla foo');
    var cs = allClasses(el);
    equal(cs.length, 2);
});

test("urljoin", function () {
    var urljoin = lux.utils.urljoin;
    equal(urljoin('bla', 'foo'), 'bla/foo', 'Got bla/foo');
    equal(urljoin('bla/', '//foo.com', '', '//', 'pippo'),
            'bla/foo.com/pippo', 'Got bla/foo.com/pippo');
    equal(urljoin('http://bla/', '//foo.com', '', '//', 'pippo'),
            'http://bla/foo.com/pippo', 'Got http://bla/foo.com/pippo');
});

module('lux.utils.logger');

test("logger", function() {
    var Logger = lux.utils.Logger;
    equal(typeof(Logger), 'function', 'Logger is a function');
    //
    var logger = new Logger();
    equal(logger.handlers.length, 0, 'No handlers');
    // Create a jquery element
    var elem = $('<div/>');
    var hnd = logger.addElement(elem);
    equal(logger.handlers.length, 1, '1 handler');
    equal(logger.handlers[0], hnd, 'handler in handlers');
    //
    logger.debug('ciao');
    var inner = elem.html();
    equal(inner, '', 'HTML handler debug');
    elem.empty();
    //
    logger.info('ciao');
    inner = elem.html();
    equal(inner, '<pre class="lux-logger info">info: ciao</pre>', 'HTML handler info');
    elem.empty();
    //
    logger.warning('ciao');
    inner = elem.html();
    equal(inner, '<pre class="lux-logger warning">warning: ciao</pre>', 'HTML handler warning');
    elem.empty();
    //
    logger.error('ciao');
    inner = elem.html();
    equal(inner, '<pre class="lux-logger error">error: ciao</pre>', 'HTML handler error');
    elem.empty();
});

module('lux.Model');

test("Class", function () {
    var Class = lux.Class;
    equal(typeof(Class), 'function', 'Class is an function');
    equal(typeof(Class.__class__), 'function', 'Class metaclass is an function');
    //
    var TestClass = Class.extend({
        hi: function () {
            return "I'm a test";
        }
    });
    var TestClass2 = TestClass.extend({
        init: function (name) {
            this.name = name;
        },
        hi: function () {
            return this._super() + " 2";
        },
        toString: function () {
            return this.name;
        }
    });
    //
    // class method
    TestClass2.create2 = function () {
        var instance = new TestClass2('create2');
        return instance;
    };
    //
    var test1 = new TestClass(),
        test2 = new TestClass2('luca');
    //
    ok(test1 instanceof TestClass, 'test1 is instance of TestClass');
    ok(test1 instanceof Class, 'test1 is instance of Class');
    ok(!(test1 instanceof TestClass2), 'test1 not an instance of TestClass2');
    ok(test2 instanceof TestClass, 'test2 is instance of TestClass');
    ok(test2 instanceof Class, 'test2 is instance of Class');
    ok(test2 instanceof TestClass2, 'test2 is an instance of TestClass2');
    //
    equal(test1.hi(), "I'm a test");
    equal(test2.hi(), "I'm a test 2");
    //
    // Test he class method
    ok(typeof(TestClass2.create2), 'function', 'TestClass2.create2 is an function');
    var test3 = TestClass2.create2();
    ok(test3 instanceof TestClass, 'test3 is instance of TestClass');
    ok(test3 instanceof Class, 'test3 is instance of Class');
    ok(test3 instanceof TestClass2, 'test3 is an instance of TestClass2');
    //
    var TestClass3 = TestClass2.extend({
        test: TestClass2,
        init: function (name, surname) {
            this._super(name);
            this.surname = surname;
        }
    });
    //
    var t3 = new TestClass3('luca', 'sbardella');
    equal(t3.test, TestClass2, 'Test class as attribute of a class');
    equal(t3.name, 'luca');
    equal(t3.surname, 'sbardella');
    equal(t3.test, TestClass2);
});


test("Type", function () {
    var Type = lux.Type,
        Class = lux.Class;
    equal(typeof(Type), 'function', 'Type is an function');
    //
    // Create a new metaclass
    var NewType = Type.extend({
        new_class: function (Prototype, attrs) {
            var cls = this._super(Prototype, attrs);
            cls.prototype.meta_attr = 'OK';
            return cls;
        }
    });
    var TestClass = Class.extend({
        Metaclass: NewType,
        hi: function () {
            return "I'm a test";
        }
    });
    equal(TestClass.prototype.meta_attr, 'OK', 'meta attribute is set');
    var test = new TestClass();
    ok(test instanceof TestClass, 'test is instance of TestClass');
    ok(test instanceof Class, 'test is instance of Class');
    equal(test.meta_attr, 'OK');
    //
    var TestClass2 = TestClass.extend({
        hi: function () {
            return this._super() + " 2";
        }
    });
    //
    var test2 = new TestClass2();
    equal(test2.meta_attr, 'OK');
    equal(test2.hi(), "I'm a test 2");
});


test("Model", function () {
    var Model = lux.Model;
    equal(typeof(Model), 'function', 'Type is an function');
    var meta = Model.prototype._meta;
    equal(Model._meta, meta, '_meta attribute available both in constructor as well as prototype');
    equal(meta.model, Model, 'meta model attribute is equal to Model');
    equal(meta.pkname, 'id');
    equal(meta.name, 'model');
    equal(meta.title, 'model');
    //
    // Create a model
    var Book = Model.extend({
        meta: {
            name: 'book'
        }
    });
    //
    meta = Book.prototype._meta;
    equal(meta.pkname, 'id');
    equal(meta.name, 'book');
    equal(meta.title, 'book');
    //
    var book = new Book({'pages': 200});
    ok(book.pk() === undefined, 'book ' + book + ' has a no pk value');
    ok(book.id(), '... it has an id value');
    ok(book.isNew(), '... it is new');
    equal(book.get('pages'), 200, '... it has 200 pages.');
    equal(book._meta, meta, '... it has same meta as constructor');
    equal(meta.live(book.id()), book, '... it is in live instances');
    equal(_.size(book.changedFields()), 0, '... no fields have changed');
    book.set('year', 200);
    equal(_.size(book.changedFields()), 1, '... fields have changed');
    //
    var Book2 = Model.extend({
    });
    var meta2 = Book2._meta;
    equal(meta2.name, 'model', 'meta attribute does not inherit.');
    //
    // Custom meta attributes
    var Page = Model.extend({
        meta: {
            name: 'page',
            plugins: {}
        }
    });
    //
    equal(Page._meta.pkname, 'id');
    equal(Page._meta.name, 'page');
    equal(Object(Page._meta.plugins), Page._meta.plugins, 'Page model has plugins attribute in meta');
});


module('lux.web.select');


test("select", function() {
    equal(typeof(web.select), 'function', 'lux.web.dialog is an function');
    var s = web.select();
    equal(s.name, 'select');
    var element = s.element();
    equal(element.prop('tagName'), 'SELECT');
    var select2 = s.select2();
    var container = s.container();
    ok(element[0] !== container[0], "Different container");
    test_destroy(s);
});

module('lux.web.dialog');

test("dialog", function() {
    equal(typeof(web.dialog), 'function', 'lux.web.dialog is an function');
    var d = web.dialog({title: 'Hello World!'});
    equal(d.name, 'dialog');
    equal(d.buttons.children().length, 0, "No buttons");
    //
    // Closable
    ok(!d.options.closable, "dialog is not closable");
    d.closable();
    ok(d.options.closable, "dialog is closable");
    equal(d.buttons.children().length, 1, "One button");
    test_destroy(d);
});

//test("dialog.movable", function() {
//    var d = web.dialog({title: 'I am movable', movable: true});
//    equal(d.element().attr('draggable'), "true", 'Draggable attribute is true');
//});
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

module('lux.cms');

test("Content", function() {
    var cms = lux.cms,
        Content = cms.Content;
    equal(Content._meta.name, 'content', 'Content meta name is content');
    Content._meta.set_transport(new lux.Storage({type: 'session'}));
    equal(Content._meta._backend.storage, sessionStorage, 'Backend on sessionStorage');
    //
    // Test Views
    var RowView = cms.RowView;
    var row = new RowView();
    ok(row instanceof cms.ContentView, 'Testing RowView class');
});
//
});