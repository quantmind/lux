define(['angular'], function (angular) {

    angular.module("luxRestApiMock", [])

        .config(['$provide', function ($provide) {

            $provide.decorator('$httpBackend', angular.mock.e2e.$httpBackendDecorator);
        }])

        .run(['$httpBackend', function ($httpBackend) {

            var api_mock_data = {
                '/api': {'authorizations_url': '/authorizations'}
            };

            for (url in api_mock_data) {
                $httpBackend.whenGET(url).respond(api_mock_data[url]);
            }
        }]);
});
