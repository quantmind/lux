import _ from '../ng';
import reverseMerge from '../core/reverseMerge';
import LuxComponent from '../lux/component';


// @ngInject
export function luxForm ($lux, $log, luxFormConfig) {

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
        link: {
            post: postLink
        }
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
        $scope.fields = {};
        $scope.info = new Form($scope, $lux, $log, luxFormConfig, $scope.json);
        $scope.field = $scope.info;
    }

    function postLink ($scope) {
        var info = $scope.info,
            action = info.action;

        if (!action || action.action != 'update') return;

        var api = $lux.api(action);
        $scope.form.$pending = true;
        api.get().then(success, failure);

        function success (response) {
            $scope.form.$pending = false;
            var data = response.data;
            _.forEach(data, function (value, key) {
                $scope.model[key] = value.id || value;
            })
        }

        function failure () {
            $scope.form.$pending = false;
        }

    }

}


// @ngInject
export function luxField ($log, $lux, luxFormConfig, luxLazy) {
    var cfg = luxFormConfig;

    return {
        restrict: 'AE',
        require: '?^luxForm',
        scope: {
            info: '=',
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

        if (!type.group) {
            if (!field.name)
                return $log.error('Field with no name attribute in lux-form');
            $scope.field = field = new Field($scope, $lux, $log, cfg, field);
            $scope.info.fields[field.name] = field;
        }

        mergeOptions(field, type.defaultOptions, $scope);
        field.fieldType = type;
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
info="info"
form="${form_id}">
</lux-field>`
}


class FormElement extends LuxComponent {

    constructor ($scope, $lux, $log, $cfg, field) {
        super($lux);
        this.$scope = $scope;
        this.$lux = $lux;
        this.$cfg = $cfg;
        this.$log = $log;
        let directives = [];
        _.forEach(field, (value, key) => {
            if (isDirective(key))
                directives.push(`${key}='${value}'`);
            else
                this[key] = value;
        });
        this.directives = directives.join(' ');
    }

    get $form () {
        return this.$scope.form;
    }

    get model () {
        return this.$scope.model;
    }
}


class Form extends FormElement {

    get fields () {
        return this.$scope.fields;
    }

    setSubmited () {
        this.$form.$setSubmitted();
        this.$form.$pending = true;
        this.$lux.messages.clear(this.id);
        _.forEach(this.fields, (field) => {
            delete field.server_message;
            delete field.server_error;
        });
    }

    addMessages (messages, level) {
        var fields = this.fields,
            formMessage = [];
        if (!_.isArray(messages)) messages = [messages];

        _.forEach(messages, (message) => {
            if (message.field && fields[message.field]) {
                if (level === 'error') {
                    fields[message.field].server_error = message.message;
                    fields[message.field].ngField.$invalid = true;
                } else
                    fields[message.field].server_message = message.message;
            } else
                formMessage.push(message);
        });

        super.addMessages(formMessage, level);
    }
}

// Logic and data for a form Field
class Field extends FormElement {

    get error () {
        var ngField = this.ngField;
        if (ngField && this.displayStatus && ngField.$invalid) {
            if (ngField.$error.required) return this.required_error || 'This field is required';
            else return this.server_error || this.validation_error || 'Not a valid value';
        }
    }

    get success () {
        if (this.displayStatus && !this.error) return true;
    }

    get displayStatus () {
        if (this.disabled || this.readonly) return false;
        var ngField = this.ngField;
        return ngField && (this.$form.$submitted || ngField.$dirty);
    }

    get ngField () {
        return this.$scope.form[this.name];
    }

    get info () {
        return this.$scope.info;
    }

    $click ($event) {
        var action = this.$cfg.getAction(this.type);
        if (action) action.call(this, $event);
    }
}


function isDirective(key) {
    var bits = key.split('-');
    if (bits.length === 2) return true;
}
