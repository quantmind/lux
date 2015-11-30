define(function(require) {

    describe("Test lux.grid module", function() {

        var $rootScope;
        var $compile;
        var modal = jasmine.createSpyObj('modal', ['show']);
        var apiMock;

        function digest(scope, template) {
            var element = $compile(template)(scope);
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
            var scope = $rootScope.$new();
            var element = digest(scope, '<div rest-grid="lux.gridTests.pGrid1"></div>');
            scope.$digest();

            expect(scope.gridOptions.permissions.UPDATE).toBe(false);
            expect(scope.gridOptions.permissions.CREATE).toBe(false);
            expect(scope.gridOptions.permissions.DELETE).toBe(false);
        });

        it('initially has only one item of the menu - column visibility', function() {
            lux.gridTests.pGrid2 = {
                "target": {"name": "dummy", "url": "dummy://url"},
            };
            var scope = $rootScope.$new();
            var element = digest(scope, '<div rest-grid="lux.gridTests.pGrid2"></div>');
            scope.$digest();

            expect(scope.gridOptions.gridMenuCustomItems.length).toBe(1);
            expect(scope.gridOptions.gridMenuCustomItems[0].title).toEqual('Columns visibility');
        });

        it('adds CREATE and DELETE permissions', function() {
            lux.gridTests.pGrid3 = {
                "target": {"name": "dummy", "url": "dummy://url"},
                "permissions": {"CREATE": true, "DELETE": true}
            };
            var scope = $rootScope.$new();
            var element = digest(scope, '<div rest-grid="lux.gridTests.pGrid3"></div>');
            scope.$digest();

            expect(scope.gridOptions.permissions.CREATE).toBe(true);
            expect(scope.gridOptions.permissions.DELETE).toBe(true);
            expect(scope.gridOptions.permissions.UPDATE).toBe(false);
            expect(scope.gridOptions.gridMenuCustomItems.length).toBe(3);
            expect(scope.gridOptions.gridMenuCustomItems[0].title).toContain('Add');
            expect(scope.gridOptions.gridMenuCustomItems[1].title).toContain('Delete');
        });

        it('check getStringOrJsonField method', function() {
            lux.gridTests.pGrid4 = {
                "target": {"name": "dummy", "url": "dummy://url"},
            };
            var scope = $rootScope.$new();
            var element = digest(scope, '<div rest-grid="lux.gridTests.pGrid4"></div>');
            scope.$digest();

            var result = scope.getStringOrJsonField({'repr': 'Field'});
            expect(result).toBe('Field');

            result = scope.getStringOrJsonField({'repr': 'Field', 'id': 'Field ID'});
            expect(result).toBe('Field');

            result = scope.getStringOrJsonField({'id': 'Field ID'});
            expect(result).toBe('Field ID');

            result = scope.getStringOrJsonField('test string');
            expect(result).toBe('test string');
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
