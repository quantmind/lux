
    describe("Test lux.nav module", function() {
        //
        var digest = function($compile, $rootScope, template) {
                var scope = $rootScope.$new(),
                    element = $compile(template)(scope);
                scope.$digest();
                return element;
            };

        beforeEach(function () {
            module('lux.nav');
        });

        it("Navigation controller", function() {

            //expect(typeof(scope.navbar)).toBe('object');
            //expect(scope.navbar.collapseWidth).toBe(768);
            //expect(scope.navbar.theme).toBe('default');
            //expect(scope.navbar.themeTop).toBe('default');
            //expect(scope.navbar.items).toBe(undefined);
            //expect(scope.navbar.items2).toBe(undefined);
        });

        it("navbar directive", inject(function($compile, $rootScope) {
            var template = '<navbar data-theme="inverse" data-id="navid3" data-top=1></navbar>',
                element = digest($compile, $rootScope, template);

            expect(element.children().length).toBe(1);
            var nav = angular.element(element.children()[0]);
            //
            expect(nav[0].tagName).toBe('NAV');
            expect(nav.hasClass('navbar')).toBe(true);
            expect(nav.hasClass('navbar-inverse')).toBe(true);
            expect(nav.hasClass('navbar-static-top')).toBe(true);
            expect(nav.hasClass('navbar-fixed-top')).toBe(false);
            expect(nav.attr('id')).toBe('navid3');
        }));

        it("navbar directive with options from object", inject(function($compile, $rootScope) {
            lux.context._navbar1 = {
                id: 'navbar1',
                theme: 'inverse',
                top: true,
                fixed: true,
                items: [{href: '/', name: 'home'},
                        {href: '/bla', name: 'bla'}]
            };
            var template = '<navbar data-options="lux.context._navbar1"></navbar>',
                element = digest($compile, $rootScope, template),
                nav = angular.element(element.children()[0]);
            delete lux.context._navbar1;
            //
            expect(nav[0].tagName).toBe('NAV');
            expect(nav.hasClass('navbar')).toBe(true);
            expect(nav.hasClass('navbar-inverse')).toBe(true);
            expect(nav.hasClass('navbar-static-top')).toBe(true);
            expect(nav.hasClass('navbar-fixed-top')).toBe(true);
            expect(nav.attr('id')).toBe('navbar1');
        }));

        it("navbar2 directive", inject(function($compile, $rootScope) {
            var element = '<navbar2></navbar2>';
            return
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
        }));
    });
