
    describe("Test lux.restapi module", function() {
        angular.module('lux.restapi.test', ['lux.loader', 'lux.restapi']);

        beforeEach(function () {
            module('lux.restapi.test');
        });

        it("Luxrest function", inject(['$rootScope', function (scope) {
            expect(_.isFunction(scope.luxrest)).toBe(true);
            var client = scope.luxrest();
            expect(client).toBe(undefined);
        }]));
    });