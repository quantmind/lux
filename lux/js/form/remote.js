import _ from '../ng';


// @ngInject
export default function ($lux) {

    return {
        restrict: 'A',
        link: link
    };

    function link (scope, element, attrs) {
        var remote = attrs.luxRemote;
        if (_.isString(remote)) remote = _.fromJson(remote);
        scope.paginator = $lux.api(remote).paginator();
        scope.paginator.getData();
    }
}


export function compileUiSelect (lazy, html, scope) {

    lazy.require(['ui-select', 'angular-sanitize'], ['ui.select', 'ngSanitize'], function () {
        html = lazy.$compile(html)(scope);
    });
}
