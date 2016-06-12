
export function luxForm () {

    return {
        restrict: 'AE',
        scope: {
            json: '=?',
            url: '=?'
        },
        controller: FieldController,
        link: linkField
    };
}


export function luxFormset () {

    return {
        restrict: 'AE',
        require: '?^luxForm',
        scope: {
            field: '=',
            formset: '=',
            model: '='
        },
        controller: FieldController,
        link: linkField
    };

}


export function luxField () {
    return {
        restrict: 'AE',
        require: '?^luxForm',
        scope: {
            field: '=',
            form: '=',
            luxform: '='
        },
        controller: FieldController,
        link: linkField
    };
}


// @ngInject
function FieldController ($scope, $lux, luxFormConfig) {
    $scope.$lux = $lux;
    var field = $scope.field || $scope.json || {},
        tag = field.tag || luxFormConfig.getTag(field.type),
        $log = $lux.$log,
        type;

    if (!tag)
        type = luxFormConfig.getType(field.type);
    else
        type = luxFormConfig.getType(tag);

    if (!type) {
        $scope.field = null;
        return $log.error(`No field type for ${tag || field.type}`);
    }

    $scope.field = new type.class($scope, $lux, luxFormConfig, field, type, tag);
}

function linkField($scope, $element) {
    if ($scope.field)
        $scope.field.$compile($scope, $element);
}
