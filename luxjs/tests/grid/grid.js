define(function(require) {

    describe("Test lux.grid module", function() {

        var $rootScope;
        var $compile;
        var modal = jasmine.createSpyObj('modal', ['show']);
        var apiMock;

        function digest(template) {
            var scope = $rootScope.$new(),
                element = $compile(template)(scope);
            scope.$digest();
            return element;
        };

        lux.gridTests = {};

        beforeEach(function () {
            apiMock = createLuxApiMock();
            var $luxMock = createLuxMock(apiMock);

            angular.mock.module('lux.grid', function($provide) {
                $provide.value('$lux', $luxMock);
                $provide.value('$modal', modal);
            });

            inject(function (_$compile_, _$rootScope_) {
                $compile = _$compile_;
                $rootScope = _$rootScope_;
            });
        });

        afterEach(function () {
        });

        it('default permissions of actions', function() {
            lux.gridTests.pGrid1 = {
                "target": {"name": "dummy", "url": "dummy://url"},
            };
            var element = digest('<div rest-grid="lux.gridTests.pGrid1"></div>');
            scope = element.scope();

            expect(scope.gridOptions.permissions.UPDATE).toBe(false);
            expect(scope.gridOptions.permissions.CREATE).toBe(false);
            expect(scope.gridOptions.permissions.DELETE).toBe(false);
        });

        it('initially has only one item of the menu - column visibility', function() {
            lux.gridTests.pGrid2 = {
                "target": {"name": "dummy", "url": "dummy://url"},
            };
            var element = digest('<div rest-grid="lux.gridTests.pGrid2"></div>');
            scope = element.scope();

            expect(scope.gridOptions.gridMenuCustomItems.length).toBe(1);
            expect(scope.gridOptions.gridMenuCustomItems[0].title).toEqual('Columns visibility');
        });

        it('adds CREATE and DELETE permissions', function() {
            lux.gridTests.pGrid3 = {
                "target": {"name": "dummy", "url": "dummy://url"},
                "permissions": {"CREATE": true, "DELETE": true}
            };
            var element = digest('<div rest-grid="lux.gridTests.pGrid3"></div>');
            scope = element.scope();

            expect(scope.gridOptions.permissions.CREATE).toBe(true);
            expect(scope.gridOptions.permissions.DELETE).toBe(true);
            expect(scope.gridOptions.permissions.UPDATE).toBe(false);
            expect(scope.gridOptions.gridMenuCustomItems.length).toBe(3);
            expect(scope.gridOptions.gridMenuCustomItems[0].title).toContain('Add');
            expect(scope.gridOptions.gridMenuCustomItems[1].title).toContain('Delete');
        });

        function createLuxMock(apiMock) {
            var $luxMock = {
                api: function() {
                    return apiMock;
                },
                window: {
                    location: {}
                }
            };

            return $luxMock;
        }

        function createLuxApiMock() {
            var apiMock = {
                get: jasmine.createSpy(),
                delete: jasmine.createSpy(),
                success: jasmine.createSpy(),
                error: jasmine.createSpy()
            };

            apiMock.get.and.returnValue(apiMock);
            apiMock.delete.and.returnValue(apiMock);
            apiMock.success.and.returnValue(apiMock);
            apiMock.error.and.returnValue(apiMock);

            return apiMock;
        }
    });
});
