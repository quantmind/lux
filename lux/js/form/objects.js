import _ from '../ng';
import LuxComponent from '../lux/component';
import {compile, asHtml, mergeOptions, mergeArray, makeChildren, fieldDirectives} from './utils';


export class FormElement extends LuxComponent {

    constructor ($scope, $lux, $cfg, field, type, tag) {
        super($lux);
        this.$cfg = $cfg;
        this.$fieldType = type;
        this.$luxform = $scope.luxform;
        this.tag = tag;
        // set name first - it may be needed by other attributes
        this.name = field.name;
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

    $compile ($scope, $element, replace) {
        var field = this,
            cfg = this.$cfg,
            $log = this.$log,
            fieldType = this.$fieldType,
            template, w;

        // TODO: we have switched off the replace flag for now has it does
        //  not work as it should, events are not propagated as they should
        replace = false;

        if (!fieldType) return;

        template = fieldType.template || '';

        if (_.isFunction(template))
            template = template(field);

        var children = field.children;

        if (_.isArray(children) && fieldType.childTpl) {
            field.children = [];
            field.$setChildren(children);
            var name = this.$luxform === this ? this.name : 'form',
                inner = fieldType.childTpl(name);
            if (template) {
                var tel = _.element(template);
                tel.append(inner);
                template = asHtml(tel);
            } else
                template = inner;
        }

        _.forEach(fieldType.wrapper, (wrapper) => {
            w = cfg.getWrapper(wrapper);
            if (w) template = w.template(template, field) || template;
            else $log.error(`Could not locate lux-form wrapper "${wrapper}" in "${field.name}" field`);
        });

        var $el;

        if (replace === false) {
            $element.html(asHtml(template));
            $el = $element.contents();
        } else {
            $el = _.element(template);
            $element.replaceWith($el);
            $element = $el;
        }

        var compileHtml = fieldType.compile || compile;
        compileHtml(this.$lux, $el, $scope);
        this.$timeout(() => {
            field.$postCompile($scope, $element);
        });
    }

    $postCompile () {}

    $click ($event) {
        var action = this.$cfg.getAction(this.click || this.type);
        if (action) action.call(this, $event);
    }

    $setChildren (children) {
        var fieldType = this.$fieldType;
        if (fieldType.childTpl)
            children = makeChildren(this, children);
        if (this.children) {
            this.children.splice(0);
            var ch = this.children;
            children.forEach((c) => {
                ch.push(c);
            });
        } else
            this.children = children;
    }

    get $last () {
        if (this.$formset)
            return this.$formset.$isLast(this);
    }

    get $count () {
        return this.$formset ? this.$formset.value.length : 1;
    }
}


export class Form extends FormElement {

    constructor ($scope, $lux, $cfg, field, type, tag) {
        super($scope, $lux, $cfg, field, type, tag);
        if (!this.children) this.$setChildren([]);
        //
        // Check if this is a nested form
        var luxform = $scope.luxform,
            formset = $scope.formset;

        $scope.luxform = this.$luxform = this;

        if (formset) {
            this.$formset = formset;
            this.model = $scope.model;
            this.tag = 'ng-form';
            this.name = formset.name + '_' + formset.counter();
            this.classes = 'form-inline formset';
        } else if (luxform) {
            this.tag = 'ng-form';
            if (!this.name)
                this.name = 'form' + $lux.id();
            if (this.flat)
                this.model = luxform.model;
            else {
                luxform.model[this.name] = {};
                this.model = luxform.model[this.name];
            }
            luxform.$setField(this);
            this.classes = 'lux-form';
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

    $setChildren (children) {
        this.fields = {};
        super.$setChildren(children);
    }

    $compile ($scope, $element) {
        super.$compile($scope, $element, false);
    }

    $postCompile ($scope, $element) {
        this.$htmlElement = $element[0];
        this.$form = $scope[this.name];

        var base = this,
            form = this.$form,
            action = this.action,
            model = this.model;

        if (!action || action.action != 'update') return;

        var api = this.$lux.api(action);
        form.$pending = true;
        api.get().then(success, failure);

        function success (response) {
            form.$pending = false;
            var data = response.data,
                current,
                field;
            _.forEach(data, function (value, key) {
                if (value !== null) {
                    current = model[key];
                    field = base.fields[key];
                    if (_.isArray(current))
                        mergeArray(current, value);
                    else if (field && field.type == 'form' && current)
                        _.extend(current, value);
                    else model[key] = value.id || value;
                }
            });
        }

        function failure () {
            form.$pending = false;
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
        fieldDirectives(this);
        this.$scope = $scope;
        this.$form = $scope.form;
        this.$luxform.$setField(this);
    }

    get error () {
        var ngField = this.ngField;
        if (ngField && this.displayStatus && ngField.$invalid) {
            var msg = this.$cfg.error(this);
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
        return this.model[this.name];
    }

    set value (value) {
        this.model[this.name] = value;
    }

    get success () {
        if (this.displayStatus && !this.error) return true;
    }

    get displayStatus () {
        var scope = this.$scope;
        if (scope.$eval(this.disabled) || scope.$eval(this.readonly)) return false;
        var ngField = this.ngField;
        return ngField && (this.$form.$submitted || ngField.$dirty);
    }

    get ngField () {
        if (this.$form)
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

    $compile ($scope, $element) {
        $scope.field = this.$formset;
        $scope.formset = this;
        super.$compile($scope, $element, false);
    }

    $newForm () {
        var model = {};
        this.value.push(model);
        return model;
    }

    $removeForm(form) {
        var index = this.value.indexOf(form.model);
        if (index > -1)
            this.value.splice(index, 1);
    }

    $isLast (form) {
        return this.value.indexOf(form.model) === this.value.length-1;
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
        theme: "danger btn-sm",
        label: "remove",
        icon: "fa fa-trash",
        title: "remove",
        hide: "field.$luxform.$count === 1",
        click: "removeForm"
    });
    form.children.push({
        tag: "a",
        theme: "default btn-sm",
        icon: "fa fa-plus",
        title: "add",
        hide: "!field.$luxform.$last",
        click: "addForm"
    });
    return form;
}
