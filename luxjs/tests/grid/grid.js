define(function(require) {

    describe("Test lux.grid module", function() {
        //
        var scope,
            element,
            modal = jasmine.createSpyObj('modal', ['show']),
            gridApi;

        var $compile,
            $rootScope,
            $httpBackend,
            GridService,
            api_mock_data = require('./mock');

        var context = {
            API_URL: '/api'
        };

        angular.module('lux.grid.test', ['lux.loader', 'lux.grid', 'lux.restapi'])
            .value('context', context);

        beforeEach(function () {
            module('lux.grid.test');

            module(function ($provide) {
                $provide.value('$modal', modal);
            });

            inject(function (_$compile_, _$rootScope_, _$httpBackend_, _GridService_) {
                $compile = _$compile_;
                $rootScope = _$rootScope_;
                $httpBackend = _$httpBackend_;
                GridService = _GridService_;
            });
        });

        afterEach(function () {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        });

        it('test grid services', function() {
            $httpBackend.expectGET('/api/metadata').respond({"default-limit": 25, "id": "id", "repr": "id", "columns": [{"name": "id", "type": "integer", "filter": true, "sortable": true, "field": "id", "displayName": "Id"}, {"name": "path", "type": "string", "filter": true, "sortable": true, "field": "path", "displayName": "Path"}, {"name": "title", "type": "string", "filter": true, "sortable": true, "field": "title", "displayName": "Title"}], "total": 3});
            $httpBackend.expectGET('/api?limit=25').respond({"result": [{"template_id": 1, "description": "test", "updated": "2015-06-25T09:35:37.486418+00:00", "id": 1, "layout": "{ \"rows\": \"[[col-md-6, col-md-6], [col-md-6, col-md-6]]\", \"components\": \"[{type:text, id:3, row:0, col:0, pos:0}, {type:text, id:4, row:1, col:1, pos:0}]\" }", "published": false, "title": "test", "path": "test"}, {"template_id": 1, "id": 2, "updated": "2015-06-25T09:36:04.162474+00:00", "layout": "{ \"rows\": \"[[col-md-6, col-md-6], [col-md-6, col-md-6]]\", \"components\": \"[{type:text, id:3, row:0, col:0, pos:0}, {type:text, id:4, row:1, col:1, pos:0}]\" }", "published": true, "title": "test2", "path": "test2"}], "total": 2});

            scope = $rootScope.$new();
            scope.luxgrids = {};
            scope.luxgrids.grid_KBnPS = {"target": {"url": "http://127.0.0.1:6050", "name": "html_pages_url"}};

            /*var element = angular.element('<div rest-grid="luxgrids.grid_kbmCz"><script>if (!this.luxgrids) {this.luxgrids = {};} this.luxgrids.grid_kbmCz = {"target": {"url": "http://127.0.0.1:6050", "name": "html_pages_url"}};</script></div>'),
                element = $compile(element)(scope),
                grid = angular.element(element.children()[0]);

            //
            expect(grid[0].tagName).toBe('DIV');
            expect(grid.hasClass('table-uigrid')).toBe(true);
            expect(element.scope().options.target).toBeDefined();
            */

            scope.gridOptions = GridService.buildOptions(scope, scope.luxgrids.grid_KBnPS);
            GridService.getInitialData(scope, scope.luxgrids.grid_KBnPS);

            $rootScope.$digest();
            $httpBackend.flush();

            // Test Options
            expect(scope.gridOptions.paginationPageSizes.length).toBe(3);
            expect(scope.gridOptions.paginationPageSize).toBe(25);
            expect(scope.gridOptions.enableFiltering).toBe(true);
            expect(scope.gridOptions.enableRowHeaderSelection).toBe(false);
            expect(scope.gridOptions.useExternalPagination).toBe(true);
            expect(scope.gridOptions.useExternalSorting).toBe(true);

            // Test ColumnDefs
            expect(scope.gridOptions.columnDefs.length).toBe(3);
            expect(scope.gridOptions.columnDefs[0].field).toBe("id");
            expect(scope.gridOptions.columnDefs[0].displayName).toBe("Id");
            expect(scope.gridOptions.columnDefs[0].type).toBe("number");

            // Test Data
            expect(scope.gridOptions.totalItems).toBe(2);
            expect(scope.gridOptions.data.length).toBe(2);
            expect(scope.gridOptions.data[0].template_id).toBe(1);
            expect(scope.gridOptions.data[0].description).toBe('test');
            expect(scope.gridOptions.data[0].id).toBe(1);
            expect(scope.gridOptions.data[0].published).toBe(false);
            expect(scope.gridOptions.data[0].title).toBe('test');
            expect(scope.gridOptions.data[0].path).toBe('test');

        });

    });

});
