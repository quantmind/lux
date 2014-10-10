
    describe("Test lux.nav module", function() {
        var scope,
            controller;

        beforeEach(function () {
            module('lux.nav');
        });

        it("Navigation controller", function() {
            //
            beforeEach(inject(function ($rootScope, $controller) {
                scope = $rootScope.$new();
                controller = $controller('Navigation', {'$scope': scope});
            }));

            afterEach(function () {
                scope.$digest();
            });

            expect(typeof(scope.navbar)).toBe('object');
            expect(scope.navbar.collapseWidth).toBe(768);
            expect(scope.navbar.theme).toBe('default');
            expect(scope.navbar.themeTop).toBe('default');
            expect(scope.navbar.items).toBe(undefined);
            expect(scope.navbar.items2).toBe(undefined);
        });

        it("navbar2 directive", function() {
            var element = '<navbar2></navbar2>';

            scope = $rootScope.$new();
            scope.items2 = [
                {href: '/', name: 'home'},
                {href: '/foo'}];
            controller = $controller('Navigation', {'$scope': scope});

            expect(scope.navbar.items2.length).toBe(2);
            element = $compile(element)(scope);
            var nav = element.find('nav');
            //
            expect(nav.parent()).toBe(element);
            expect(nav.hasClass('navbar')).toBe(true);
            expect(nav.hasClass('navbar-default')).toBe(true);

            expect(scope.navbar.collapseWidth).toBe(768);
        });
    });