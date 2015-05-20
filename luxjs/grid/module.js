    //
    //  Module for interacting with API to fetch model data and display it
    angular.module('lux.grid', ['ngTouch', 'ui.grid'])
        //
        .service('gridService', ['$lux', function ($lux, $http) {

            String.prototype.capitalize = function() {
                return this.charAt(0).toUpperCase() + this.slice(1);
            };

            this.buildColumnDefs = function(fields) {
                var columns = [];

                angular.forEach(fields, function(_, key) {
                    columns.push({
                        field: key,
                        displayName: key.split('_').join(' ').capitalize()
                    });
                });

                return columns;
            };

            this.getModelUrl = function() {
                var loc = window.location,
                    path = loc.pathname,
                    modelname = path.split('/').pop(-1);

                return modelname + '_url';
            };

        }])
        //
        .controller('RestGrid', ['$scope', '$lux', 'gridService', function (scope, $lux, gridService) {

            var modelUrl = gridService.getModelUrl(),
                client = scope.api(),
                target = {
                    url: scope.API_URL,
                    name: modelUrl
                };

            scope.gridOptions = {
                data: [],
                columnDefs: []
            };

            client.get(target).success(function(data) {
                scope.gridOptions.data = data;
                scope.gridOptions.columnDefs = gridService.buildColumnDefs(data[0]);
            });

        }]);
