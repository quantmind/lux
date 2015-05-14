
    angular.module("lux.grid.mock", [])

        .config(['$provide', function ($provide) {

            $provide.decorator('$httpBackend', angular.mock.e2e.$httpBackendDecorator);
        }])

        .run(['$httpBackend', function ($httpBackend) {

            var api_mock_data = {
                '/user': {
                    'columns': [
                        {field: 'id', displayName: 'ID'},
                        {field: 'user', displayName: 'user'},
                        {field: 'edit', cellTemplate: '<div><button class="btn btn-primary" ng-click=" getExternalScopes().onClick(row.entity.fullName)">Edit</button></div>'}
                    ],
                    'rows': [{
                        'id': 1,
                        'user': 'Marius',
                    }, {
                        'id': 2,
                        'user': 'Adam',
                    }]
                },
                '/group': {
                    'columns': [
                        {field: 'id', displayName: 'ID'},
                        {field: 'group', displayName: 'Group'}
                    ],
                    'rows': [{
                        'id': 1,
                        'group': 'Admins',
                    }, {
                        'id': 2,
                        'group': 'Staff',
                    }]
                },
                '/exchange': {
                    'columns': [
                        {field: 'id', displayName: 'ID'},
                        {field: 'exchange', displayName: 'Exchange'},
                        {field: 'price', displayName: 'Price'}
                    ],
                    'rows': [{
                        'id': 1,
                        'exchange': 'BATS',
                        'price': 100,
                    }, {
                        'id': 2,
                        'exchange': 'ERIS',
                        'price': 200,
                    }]
                }
            };

            for (var url in api_mock_data) {
                $httpBackend.whenGET(url).respond(api_mock_data[url]);
            }
        }]);
