

export default function () {

    return {
        restrict: 'AE',
        scope: {
            gridOptions: '=?'
        },
        controller: GridController,
        link: link
    };

    // @ngInject
    function GridController ($scope, $lux) {
        $scope.grid = $lux.grid($scope.gridOptions);
    }

    function link ($scope, element) {
        $scope.grid.$onLink($scope, element);
    }
}
