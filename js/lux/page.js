

    lux.controllers.controller('page', ['$scope', '$http', '$location', function ($scope, $http, $location) {
        angular.extend($scope, context);
        $scope.search_text = '';

        // logout via post method
        $scope.logout = function(e, url) {
            e.preventDefault();
            e.stopPropagation();
            $.post(url).success(function (data) {
                if (data.redirect)
                    window.location.replace(data.redirect);
            });
        };

        // Search
        $scope.search = function () {
            if ($scope.search_text) {
                window.location.href = '/search?' + $.param({q: $scope.search_text});
            }
        };

    }]);