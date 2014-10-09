
    describe("Test lux.nav module", function() {
        //beforeEach(angular.module('app'));
        beforeEach(function () {
            module('lux.nav');
        });

        it("Navigation controller", function() {
            var scope,
                controller;
            beforeEach(inject(function ($rootScope, $controller) {
                scope = $rootScope.$new();
                controller = $controller('Navigation', {'$scope': scope});
            }));

            expect(typeof(scope.navbar)).toBe('object');
            expect(scope.navbar.collapseWidth).toBe(768);
            expect(scope.navbar.theme).toBe('default');
        });
    });