

export default function () {

    return {
        restrict: 'AE',
        scope: {
            grid: '=?'
        },
        controller: GridController,
        link: link
    };

    // @ngInject
    function GridController ($scope, luxGrid) {
        $scope.grid = luxGrid($scope.grid)
    }
    
    function link ($scope, element) {
        $scope.grid.$onLink($scope, element);
    }
}
