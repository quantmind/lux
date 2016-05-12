import _ from '../ng';
import {parseOptions} from './utils';

// @ngInject
export default function ($lux) {

    return {
        restrict: 'A',
        link: link
    };

    function link (scope, element, attrs) {
        var remote = attrs.luxRemote;
        if (_.isString(remote)) remote = _.fromJson(remote);
        var field = scope.field;
        if (!field) scope.field = field = {};
        field.paginator = $lux.api(remote).paginator();
        remoteOptions(field);
    }
}


export function compileUiSelect (lazy, html, scope) {

    lazy.require(['angular-ui-select', 'angular-sanitize'], ['ui.select', 'ngSanitize'], function () {
        html = lazy.$compile(html)(scope);
    });
}


function remoteOptions (field) {
    var params = field.paginator.api.$defaults,
        id = params.id_field,
        repr = params.repr_field;

    getData();

    function getData() {
        var placeholder = field.placeholder;
        field.placeholder = 'Loading data...';

        field.paginator.getData(function (data) {
            field.placeholder = placeholder;
            parseOptions(field, data, parseEntry);
        });
    }

    function parseEntry (entry) {
        return {
            value: entry[id],
            label: entry[repr]
        };
    }
}
