    //
    describe("Test lux class", function() {
        var Class = lux.Class;

        it("Check basic properties", function() {
            expect(typeof(Class)).toBe('function');
            expect(typeof(Class.__class__)).toBe('function');
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
            expect(test1 instanceof TestClass).toBe(true);
            expect(test1 instanceof Class).toBe(true);
            expect(test1 instanceof TestClass2).toBe(false);
            expect(test2 instanceof TestClass).toBe(true);
            expect(test2 instanceof Class).toBe(true);
            expect(test2 instanceof TestClass2).toBe(true);
            //
            expect(test1.hi()).toBe("I'm a test");
            expect(test2.hi()).toBe("I'm a test 2");
            //
            // Test he class method
            expect(typeof(TestClass2.create2), 'function', 'TestClass2.create2 is an function');
            var test3 = TestClass2.create2();
            expect(test3 instanceof TestClass, 'test3 is instance of TestClass');
            expect(test3 instanceof Class, 'test3 is instance of Class');
            expect(test3 instanceof TestClass2, 'test3 is an instance of TestClass2');
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
            expect(t3.test).toBe(TestClass2);
            expect(t3.name).toBe('luca');
            expect(t3.surname).toBe('sbardella');
            expect(t3.test).toBe(TestClass2);
        });
    });