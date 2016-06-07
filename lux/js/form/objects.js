import _ from '../ng';
import {compile, asHtml, mergeOptions} from './utils';


export function fieldInnerTemplate (formName) {
    return `<lux-field ng-repeat="child in field.children" field="child" luxform="luxform" form="${formName}"></lux-field>`
}


export class FormElement {

    constructor ($scope, $lux, $cfg, field, type, tag) {
        this.$id = $lux.id();
        this.$cfg = $cfg;
        this.$log = $lux.$log;
        this.$fieldType = type;
        this.$luxform = $scope.luxform;
        this.tag = tag;
        let directives = [];
        _.forEach(field, (value, key) => {
            if (isDirective(key))
                directives.push(`${key}='${value}'`);
            else if (key.substring(0, 1) !== '$')
                this[key] = value;
        });
        this.directives = directives.join(' ');
        mergeOptions(this, type.defaultOptions, $scope);
    }

    $compile ($scope, $element) {
        var field = this,
            cfg = this.$cfg,
            $log = this.$log,
            fieldType = this.$fieldType,
            template, w;

        if (!fieldType) return;

        template = fieldType.template || '';

        if (_.isFunction(template))
            template = template(field);

        var children = field.children;

        if (_.isArray(children) && children.length) {
            //field.children = makeChildren(children);
            var inner = fieldInnerTemplate($scope.luxform.name);
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

        $element.html(asHtml(template));
        var compileHtml = fieldType.compile || compile;
        compileHtml($scope.$lux, $element.contents(), $scope);

        //var $el = _.element(template);
        //$element.replaceWith($el);
        //var compileHtml = fieldType.compile || compile;
        //compileHtml(this.$lux, $el, $scope);
    }

    $click ($event) {
        var action = this.$cfg.getAction(this.type);
        if (action) action.call(this, $event);
    }
}


export class Form extends FormElement {

    constructor ($scope, $lux, $cfg, field, type, tag) {
        super($scope, $lux, $cfg, field, type, tag);
        this.fields = {};
        $scope.luxform = this.$luxform = this;
        // Check if this is a nested form
        var formset = $scope.formset;

        if (formset) {
            this.model = $scope.model;
            this.$formset = formset;
            this.tag = 'ng-form';
            this.name = formset.name + '_' + formset.counter();
            this.classes = 'form-inline formset';
        } else {
            this.model = {};
            this.tag = 'form';
            this.name = $scope.name || 'form';
            this.classes = 'lux-form';
        }
    }

    setSubmited () {
        this.$form.$setSubmitted();
        this.$form.$pending = true;
        this.$lux.messages.clear(this.$id);
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

    $compile ($scope, $element) {
        super.$compile($scope, $element);

        if (this.$formset)

        var action = this.action;

        if (!action || action.action != 'update') return;

        var api = $scope.$lux.api(action);
        $scope.$form.$pending = true;
        api.get().then(success, failure);

        function success (response) {
            $scope.$form.$pending = false;
            var data = response.data;
            _.forEach(data, function (value, key) {
                if (value !== null)
                    $scope.model[key] = value.id || value;
            })
        }

        function failure () {
            $scope.$form.$pending = false;
        }
    }

    $setField (field) {
        if (!field.name)
            this.$log.error('Field with no name attribute in lux-form');
        else {
            if (!this.$form)
                this.$form = field.$form;
            this.fields[field.name] = field;
        }
    }
}

// Logic and data for a form Field
export class Field extends FormElement {

    constructor ($scope, $lux, $cfg, field, type, tag) {
        super($scope, $lux, $cfg, field, type, tag);
        this.$form = $scope.form;
        this.$luxform.$setField(this);
    }

    get error () {
        var ngField = this.ngField;
        if (ngField && this.displayStatus && ngField.$invalid) {
            var msg = this.$cfg.error(ngField);
            return this.server_error || msg || 'Not a valid value';
        }
    }

    tostring () {
        return `${this.tag}.${this.name}`;
    }

    get model () {
        return this.$luxform.model;
    }

    get value () {
        return this.model[this.name]
    }

    set value (value) {
        this.model[this.name] = value;
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
        return this.$form[this.name];
    }
}

// Logic and data for a Formset
export class Formset extends FormElement {

    constructor ($scope, $lux, $cfg, field, type, tag) {
        super($scope, $lux, $cfg, field, type, tag);
        this.value = [{}];
        this.$formset = createFormset(field);
        this.$counter = 0;
        this.$formset.type = 'form';
        delete this.children;
        this.$luxform.model[this.name] = this.value;
    }

    counter () {
        return this.$counter++;
    }

    newModel () {
        var model = {};
        this.value.push(model);
        return model;
    }

    $compile ($scope, $element) {
        $scope.field = this.$formset;
        $scope.formset = this;
        super.$compile($scope, $element);
    }
}

function isDirective(key) {
    var bits = key.split('-');
    if (bits.length === 2) return true;
}


// Create the formset form the field entries
function createFormset (form) {
    form.children.push({
        tag: "a",
        theme: "danger btn-xs",
        label: "remove",
        icon: "fa fa-trash",
        title: "remove",
        click: "removeForm"
    });
    form.children.push({
        tag: "a",
        theme: "default btn-xs",
        icon: "fa fa-plus",
        title: "add",
        click: "addForm"
    });
    return form;
}
