define(['angular',
        'lux',
        'lux/testing',
        'tests/mocks/http',
        'lux/grid/rest'], function (angular, lux, tests, api_mock_data) {
    'use strict';

    describe('Test lux.grid module', function() {

        var target = {'name': 'users_url', 'url': '/api'},
            $lux, $rootScope, $httpBackend;

        angular.module('lux.grid.rest.test', ['lux.loader', 'lux.mocks.http',
            'lux.grid', 'lux.grid.rest'])
            .value('context', {API_URL: '/api'});

        beforeEach(function () {
            module('lux.grid.rest.test');

            inject(function (_$lux_, _$rootScope_, _$httpBackend_) {
                $lux = _$lux_;
                $rootScope = _$rootScope_;
                $httpBackend = _$httpBackend_;
            });
        });

        lux.gridTests = {};

        it('default permissions of actions', function () {
            lux.gridTests.pGrid1 = {target: target};

            var element = tests.digest($lux.compile, $rootScope, '<div lux-grid="lux.gridTests.pGrid1"></div>'),
                scope = element.scope(),
                grid = getGrid(scope),
                metadata = api_mock_data['/api/users/metadata'];

            expect(grid.metaFields['id']).toBe(metadata['id']);
            expect(grid.permissions.update).toBe(false);
            expect(grid.permissions.create).toBe(false);
            expect(grid.permissions.delete).toBe(false);
        });

        it('initially has only one item of the menu - column visibility', function () {
            lux.gridTests.pGrid2 = {target: target};

            var element = tests.digest($lux.compile, $rootScope, '<div lux-grid="lux.gridTests.pGrid2"></div>'),
                scope = element.scope();

            expect(scope.gridOptions.gridMenuCustomItems.length).toBe(1);
            expect(scope.gridOptions.gridMenuCustomItems[0].title).toEqual('Columns visibility');
        });

        it('adds create and delete permissions', function () {
            lux.gridTests.pGrid3 = {
                target: target,
                permissions: {'create': true, 'delete': true}
            };

            var element = tests.digest($lux.compile, $rootScope, '<div lux-grid="lux.gridTests.pGrid3"></div>'),
                scope = element.scope();

            expect(scope.gridOptions.permissions.create).toBe(true);
            expect(scope.gridOptions.permissions.delete).toBe(true);
            expect(scope.gridOptions.permissions.update).toBe(false);
            expect(scope.gridOptions.gridMenuCustomItems.length).toBe(3);
            expect(scope.gridOptions.gridMenuCustomItems[0].title).toContain('Add');
            expect(scope.gridOptions.gridMenuCustomItems[1].title).toContain('Delete');
        });

        it('check getStringOrJsonField method', function () {
            lux.gridTests.pGrid4 = {target: target};

            var element = tests.digest($lux.compile, $rootScope, '<div lux-grid="lux.gridTests.pGrid4"></div>'),
                scope = element.scope();

            var result = scope.getStringOrJsonField({'repr': 'Field'});
            expect(result).toBe('Field');

            result = scope.getStringOrJsonField({
                'repr': 'Field',
                'id': 'Field ID'
            });
            expect(result).toBe('Field');

            result = scope.getStringOrJsonField({'id': 'Field ID'});
            expect(result).toBe('Field ID');

            result = scope.getStringOrJsonField('test string');
            expect(result).toBe('test string');
        });

        function getGrid(scope) {
            var grid = scope.grid;
            expect(angular.isObject(grid)).toBe(true);
            expect(angular.isObject(grid.options)).toBe(true);
            expect(grid.scope).toBe(scope);
            $httpBackend.flush(2);
            expect(scope.grid).not.toBe(grid);
            expect(scope.grid.lux).toBe(grid);
            expect(scope.grid).toBe(grid.api);
            expect(grid.options).toBe(scope.grid.grid.options);
            $httpBackend.flush(1);
        }
    });
});
