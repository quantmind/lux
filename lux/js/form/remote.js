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


export function selectOptions (items) {
    if (!_.isArray(items)) return [];
    return items.map((opt) => {
        if (_.isArray(opt)) {
            opt = {
                value: opt[0],
                label: opt[1] || opt[0]
            }
        }
        return opt;
    });
}


export function compileUiSelect (lazy, html, scope) {

    lazy.require(['angular-ui-select', 'angular-sanitize'], ['ui.select', 'ngSanitize'], function () {
        lazy.$compile(html)(scope);
    });
}
