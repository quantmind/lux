    var jasmine = jasmineRequire.core(jasmineRequire);
    //Since this is being run in a browser and the results should populate to an HTML page,
    //require the HTML-specific Jasmine code, injecting the same reference.
    jasmineRequire.html(jasmine);

    var env = jasmine.getEnv();

    var jasmineInterface = {
        describe: function(description, specDefinitions) {
          return env.describe(description, specDefinitions);
        },

        xdescribe: function(description, specDefinitions) {
          return env.xdescribe(description, specDefinitions);
        },

        it: function(desc, func) {
          return env.it(desc, func);
        },

        xit: function(desc, func) {
          return env.xit(desc, func);
        },

        beforeEach: function(beforeEachFunction) {
          return env.beforeEach(beforeEachFunction);
        },

        afterEach: function(afterEachFunction) {
          return env.afterEach(afterEachFunction);
        },

        expect: function(actual) {
          return env.expect(actual);
        },

        pending: function() {
          return env.pending();
        },

        spyOn: function(obj, methodName) {
          return env.spyOn(obj, methodName);
        },

        addCustomEqualityTester: function(tester) {
          env.addCustomEqualityTester(tester);
        },

        jsApiReporter: new jasmine.JsApiReporter({
          timer: new jasmine.Timer()
        })
    };

    if (typeof window === "undefined" && typeof exports === "object") {
        extend(exports, jasmineInterface);
    } else {
        extend(window, jasmineInterface);
    }
