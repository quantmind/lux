import _ from '../ng';
import {getOptions} from '../core/utils';
import reverseMerge from '../core/reverseMerge';


// @ngInject
export function luxForm ($lux, $window) { //, $compile, luxFormConfig) {

    return {
        restrict: 'AE',
        replace: true,
        template: formTemplate,
        link: linkForm
    };

    function formTemplate (el, attrs) {
        var form  = getForm(attrs);
        return `<form class="lux-form" name="${form.id}" role="form" novalidate>
<lux-field ng-repeat="field in luxform.children"</lux-field>
</form>`;
    }

    function getForm (attrs) {
        var form = getOptions($window, attrs, 'luxForm');
        if (form.json) {
            form = _.fromJson(form.json);
        }
        if (form.href) {
            $lux.api(form.href).get().then(function (data) {
                _.extend(form, data);
                form.hrefData = true;
                formLink(scope, element, form);
            }, function (msg) {
                $lux.messages.error(msg)
            });
            return;
        }
        attrs.form = form;
        form.id = 'form'; // form.id || luxFormConfig.id();
        form.fields = {}
        return form;
    }

    function linkForm (scope, element, attrs) {
        var form = attrs.form;
        scope.model = {};
        scope.luxform = form;
    }

}


// @ngInject
export function luxField ($log, $compile, luxFormConfig) {
    var cfg = luxFormConfig;

    return {
        restrict: 'AE',
        require: '?^luxForm',
        link: linkField
    };

    // @ngInject
    function linkField ($scope, element) {
        var field = $scope.field,
            tag = field.tag || cfg.getTag(field.type);

        if (!tag)
            return $lux.error('Could not find a tag for field');

        field.id = field.id || cfg.id();
        field.tag = tag;
        var type = cfg.getType(field.tag);

        if (!type)
            return $log.error(`No field type for ${field.tag}`);

        mergeOptions(field, type.defaultOptions, $scope);
        field.fieldType = type;

        var template = type.template || '',
            w;

        if (!type.group) {
            if (!field.name)
                return $log.error('Field with no name attribute in lux-form');
            $scope.luxform.fields[field.name] = field;
        }

        if (_.isFunction(template))
            template = template(field);

        _.forEach(type.wrapper, (wrapper) => {
            w = cfg.getWrapper(wrapper);
            if (w) template = w.template(template) || template;
            else $log.error(`Could not locate lux-form wrapper "${wrapper}" in "${type.name}" field`);
        });

        var inner = $compile(template)($scope);
        element.append(inner);
    }

    function mergeOptions(field, defaults, $scope) {
        if (_.isFunction(defaults)) defaults = defaults(field, $scope);
        reverseMerge(field, defaults);
    }
}


