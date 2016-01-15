define(['angular',
        'lux',
        'tests/mocks/utils',
        'lux/forms'], function (angular, lux) {
    "use strict";

    describe('Remote options', function () {
        // Define the tree test module
        angular.module('bmll.remote.test', ['bmll.remote']);

        var $controller,
            $compile,
            $rootScope,
            $httpBackend,
            utils = {
                /**
                 * Call click event on element (for PhantomJS)
                 * http://stackoverflow.com/questions/15739263/phantomjs-click-an-element
                 * @param element
                 */
                click: function (element) {
                    var ev = document.createEvent("MouseEvent");
                    ev.initMouseEvent(
                        "click",
                        true, /* bubble */
                        true, /* cancelable */
                        window, null,
                        0, 0, 0, 0, /* coordinates */
                        false, false, false, false, /* modifier keys */
                        0 /*left*/,
                        null
                    );
                    element.dispatchEvent(ev);
                },
                /**
                 * Force end of all transitions for unit tests
                 * https://github.com/mbostock/d3/issues/1789
                 */
                flushAllD3Transitions: function () {
                    var now = Date.now;
                    Date.now = function () {
                        return Infinity;
                    };
                    d3.timer.flush();
                    Date.now = now;
                }
            },
            api_mock_data = {
                '/': {
                    "groups_url": "http://127.0.0.1:6050/groups",
                    "users_url": "http://127.0.0.1:6050/users",
                    "securities_url": "http://127.0.0.1:6050/securities",
                    "user_url": "http://127.0.0.1:6050/user",
                    "orderbook_url": "http://127.0.0.1:6050/orderbook",
                    "authorizations_url": "http://127.0.0.1:6050/authorizations",
                    "permissions_url": "http://127.0.0.1:6050/permissions",
                    "security_classes_url": "http://127.0.0.1:6050/security_classes",
                    "exchanges_url": "http://127.0.0.1:6050/exchanges"
                },
                '/exchanges_url': {
                    'result': [{
                        'id': '1',
                        'name': 'item 1'
                    }, {
                        'id': '2',
                        'name': 'item 2'
                    }]
                }
            };

        beforeEach(module('bmll.remote.test'));

        // Store references to $rootScope and $compile
        // so they are available to all tests in this describe block
        beforeEach(inject(function (_$controller_, _$compile_, _$rootScope_, _$httpBackend_) {
            // The injector unwraps the underscores (_) from around the parameter names when matching
            $controller = _$controller_;
            $compile = _$compile_;
            $rootScope = _$rootScope_;
            $httpBackend = _$httpBackend_;
        }));

        afterEach(function () {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        });

        if ('has two options', function () {
                $rootScope.treeOptions = treeOptions;
                for (url in api_mock_data) {
                    $httpBackend.when('GET', lux.context.API_URL + url).respond(api_mock_data[url]);
                }
                var element = angular.element('<div data-bmll-remoteoptions data-bmll-remoteoptions-name="exchanges_url"></div>');
                element = $compile(element)($rootScope);
                $rootScope.$digest();
                $httpBackend.flush();

                expect(element.scope().exchanges_url.length).toBe(2);

            });
    });

});
