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
    equal(typeof(Model), 'function', 'Model is an function');
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

