define(['lux',
        'tests/mocks/utils',
        'lux/grid'], function (lux, tests) {
    'use strict';

    describe('Test lux.grid module', function() {

        // var modal = jasmine.createSpyObj('modal', ['show']);

        lux.gridTests = {};

        it('default permissions of actions',
            inject(function ($compile, $rootScope) {
                lux.gridTests.pGrid1 = {
                    'target': {'name': 'dummy', 'url': 'dummy://url'}
                };
                var element = tests.digest($compile, $rootScope, '<div rest-grid="lux.gridTests.pGrid1"></div>'),
                    scope = element.scope();

                expect(scope.gridOptions.permissions.update).toBe(false);
                expect(scope.gridOptions.permissions.create).toBe(false);
                expect(scope.gridOptions.permissions.delete).toBe(false);
            })
        );

        it('initially has only one item of the menu - column visibility',
            inject(function ($compile, $rootScope) {
                lux.gridTests.pGrid2 = {
                    'target': {'name': 'dummy', 'url': 'dummy://url'}
                };

                var element = tests.digest($compile, $rootScope, '<div rest-grid="lux.gridTests.pGrid2"></div>'),
                    scope = element.scope();

                expect(scope.gridOptions.gridMenuCustomItems.length).toBe(1);
                expect(scope.gridOptions.gridMenuCustomItems[0].title).toEqual('Columns visibility');
            })
        );

        it('adds create and delete permissions',
            inject(function ($compile, $rootScope) {

                lux.gridTests.pGrid3 = {
                    'target': {'name': 'dummy', 'url': 'dummy://url'},
                    'permissions': {'create': true, 'delete': true}
                };

                var element = tests.digest($compile, $rootScope, '<div rest-grid="lux.gridTests.pGrid3"></div>'),
                    scope = element.scope();

                expect(scope.gridOptions.permissions.create).toBe(true);
                expect(scope.gridOptions.permissions.delete).toBe(true);
                expect(scope.gridOptions.permissions.update).toBe(false);
                expect(scope.gridOptions.gridMenuCustomItems.length).toBe(3);
                expect(scope.gridOptions.gridMenuCustomItems[0].title).toContain('Add');
                expect(scope.gridOptions.gridMenuCustomItems[1].title).toContain('Delete');
            })
        );

        it('check getStringOrJsonField method',
            inject(function ($compile, $rootScope) {
                lux.gridTests.pGrid4 = {
                    'target': {'name': 'dummy', 'url': 'dummy://url'}
                };
                var element = tests.digest($compile, $rootScope, '<div rest-grid="lux.gridTests.pGrid4"></div>'),
                    scope = element.scope();

                var result = scope.getStringOrJsonField({'repr': 'Field'});
                expect(result).toBe('Field');

                result = scope.getStringOrJsonField({'repr': 'Field', 'id': 'Field ID'});
                expect(result).toBe('Field');

                result = scope.getStringOrJsonField({'id': 'Field ID'});
                expect(result).toBe('Field ID');

                result = scope.getStringOrJsonField('test string');
                expect(result).toBe('test string');
            })
        );

    });
});
