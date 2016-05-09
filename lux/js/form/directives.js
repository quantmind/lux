import _ from '../ng';
import reverseMerge from '../core/reverseMerge';


// @ngInject
export function luxForm ($lux) {

    return {
        restrict: 'AE',
        replace: true,
        transclude: true,
        scope: {
            'json': '=?',
            'model': '=?'
        },
        template: formTemplate,
        controller: FormController,
        link: linkForm
    };

    function formTemplate (el, attrs) {
        var href = attrs.href;

        if (href && !attrs.json) {
            return $lux.api(href).get().then(function (data) {
                attrs.json = data;
                return formTemplate(el, attrs);
            }, function (msg) {
                $lux.messages.error(msg)
            });
        }

        var form_id = attrs.id || 'form',
            inner = innerTemplate(form_id);

        return `<form class="lux-form" name="${form_id}" role="form" novalidate>
${inner}
<div ng-transclude></div>
</form>`;
    }

    // ngInject
    function FormController ($scope) {
        $scope.model = {};  // model values
        $scope.fields = {};  //field container
        $scope.field = $scope.json;  // currenct field (form)
    }

    function linkForm ($scope) {
        $scope.form.$action = $scope.field.action;
    }

}


// @ngInject
export function luxField ($log, $lux, luxFormConfig, luxLazy) {
    var cfg = luxFormConfig;

    return {
        restrict: 'AE',
        require: '?^luxForm',
        scope: {
            fields: '=',
            model: '=',
            form: '=',
            field: '='
        },
        controller: FieldController,
        link: linkField
    };

    // @ngInject
    function FieldController ($scope) {
        var field = $scope.field,
            tag = field.tag || cfg.getTag(field.type);

        if (!tag)
            return $log.error('Could not find a tag for field');

        field.id = field.id || cfg.id();
        field.tag = tag;

        var type = cfg.getType(field.tag);

        if (!type)
            return $log.error(`No field type for ${field.tag}`);

        mergeOptions(field, type.defaultOptions, $scope);
        field.fieldType = type;

        if (!type.group) {
            if (!field.name)
                return $log.error('Field with no name attribute in lux-form');
            $scope.field = new Field($scope, $log, $lux, cfg, field);
            $scope.fields[field.name] = $scope.field;
        }
    }

    function linkField(scope, el) {
        var field = scope.field,
            fieldType = field.fieldType,
            template, w;

        if (!fieldType) return;

        template = fieldType.template || '';

        if (_.isFunction(template))
            template = template(field);

        var children = field.children;

        if (_.isArray(children) && children.length) {
            var inner = innerTemplate('form');
            if (template) {
                var tel = _.element(template);
                tel.append(inner);
                template = asHtml(tel);
            } else
                template = inner;
        }

        _.forEach(fieldType.wrapper, (wrapper) => {
            w = cfg.getWrapper(wrapper);
            if (w) template = w.template(template) || template;
            else $log.error(`Could not locate lux-form wrapper "${wrapper}" in "${field.name}" field`);
        });

        el.html(asHtml(template));
        var compileHtml = fieldType.compile || compile;
        compileHtml(luxLazy, el.contents(), scope);
    }

    function mergeOptions(field, defaults, $scope) {
        if (_.isFunction(defaults)) defaults = defaults(field, $scope);
        reverseMerge(field, defaults);
    }

    // sort-of stateless util functions
    function asHtml(el) {
        const wrapper = _.element('<a></a>');
        return wrapper.append(el).html();
    }

    function compile(lazy, html, scope) {
        lazy.$compile(html)(scope);
    }
}


function innerTemplate (form_id) {
    return `<lux-field ng-repeat="child in field.children"
field="child"
model="model"
fields="fields"
form="${form_id}">
</lux-field>`
}

// Logic and data for a form Field
class Field {

    constructor ($scope, $log, $lux, cfg, field) {
        this.$scope = $scope;
        this.$log = $log;
        this.$lux = $lux;
        this.$cfg = cfg;
        let directives = [];
        _.forEach(field, (value, key) => {
            if (isDirective(key))
                directives.push(`${key}='${value}'`);
            else
                this[key] = value;
        });
        this.directives = directives.join(directives);

    }

    get error () {
        var ngField = this.ngField;
        if (this.displayStatus && ngField.$invalid) {
            if (ngField.$error.required) return this.required_error || 'This field is required';
            else return this.validation_error || 'Not a valid value';
        }
    }

    get success () {
        if (this.displayStatus && !this.error) return true;
    }

    get displayStatus () {
        return this.$form.$submitted || this.ngField.$dirty;
    }

    $click ($event) {
        var action = this.$cfg.getAction(this.type);
        if (action) action.call(this, $event);
    }

    get $form () {
        return this.$scope.form;
    }

    get ngField () {
        return this.$scope.form[this.name];
    }
}


function isDirective(key) {
    var bits = key.split('-');
    if (bits.length === 2) return true;
}
