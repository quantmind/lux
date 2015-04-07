
    describe("Test lux.restapi module", function() {

        angular.module('lux.restapi.test', ['lux.loader', 'lux.restapi', 'lux.restapi.mock']);

        beforeEach(function () {
            module('lux.restapi.test');
        });

        it("Luxrest function", inject(['$rootScope', function (scope) {
            expect(_.isFunction(scope.luxrest)).toBe(true);
            var client = scope.luxrest();
            expect(client).toBe(undefined);
        }]));

        it("Luxrest object", inject(['$rootScope', function (scope) {
            expect(_.isFunction(scope.luxrest)).toBe(true);
            var client = scope.luxrest('/api');

            expect(client.name).toBe('luxrest');
            expect(client.url()).toBe('/api');

        }]));
    });