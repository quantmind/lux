
    describe("Test lux.grid module", function() {
        var context = {
            API_URL: '/api'
        };

        angular.module('lux.grid.test', ['lux.loader', 'lux.restapi', 'lux.grid.mock'])
            .value('context', context);

        beforeEach(module('lux.grid.test'));

        it("Grid api object", inject(['$rootScope', function (scope) {
            expect(_.isFunction(scope.api)).toBe(true);
            var client = scope.api();
            expect(_.isObject(client)).toBe(true);
            expect(client.baseUrl()).toBe('/api');
        }]));

    });
