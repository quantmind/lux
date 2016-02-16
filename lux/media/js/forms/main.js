define(['angular',
        'lux/main',
        'lux/forms/process',
        'lux/forms/utils',
        'lux/forms/handlers'], function (angular, lux, formProcessors) {
    'use strict';

    var extend = angular.extend,
        forEach = angular.forEach,
        extendArray = lux.extendArray,
        isString = lux.isString,
        isObject = lux.isObject,
        isArray = lux.isArray,
        baseAttributes = ['id', 'name', 'title', 'style'],
        inputAttributes = extendArray([], baseAttributes, [
            'disabled', 'readonly', 'type', 'value', 'placeholder',
            'autocapitalize', 'autocorrect']),
        textareaAttributes = extendArray([], baseAttributes, [
            'disabled', 'readonly', 'placeholder', 'rows', 'cols']),
        buttonAttributes = extendArray([], baseAttributes, ['disabled']),
        // Don't include action in the form attributes
        formAttributes = extendArray([], baseAttributes, [
            'accept-charset', 'autocomplete',
            'enctype', 'method', 'novalidate', 'target']),
        validationAttributes = ['minlength', 'maxlength', 'min', 'max', 'required'],
        ngAttributes = ['disabled', 'minlength', 'maxlength', 'required'],
        formid = function () {
            return 'f' + lux.s4();
        };

    lux.forms = {
        overrides: [],
        directives: [],
        processors: formProcessors
    };

    function extendForm (form, form2) {
        form = extend({}, form, form2);
        lux.forms.overrides.forEach(function (override) {
            override(form);
        });
        return form;
    }
    //
    // Form module for lux
    //
    //  Forms are created form a JSON object
    //
    //  Forms layouts:
    //
    //      - default
    //      - inline
    //      - horizontal
    //
    //  Events:
    //
    //      formReady: triggered once the form has rendered
    //          arguments: formmodel, formscope
    //
    //      formFieldChange: triggered when a form field changes:
    //          arguments: formmodel, field (changed)
    //
    angular.module('lux.form', ['lux.form.utils', 'lux.form.handlers', 'lux.form.process'])
        //
        .constant('formDefaults', {
            // Default layout
            layout: 'default',
            // for horizontal layout
            labelSpan: 2,
            debounce: 500,
            showLabels: true,
            novalidate: true,
            //
            dateTypes: ['date', 'datetime', 'datetime-local'],
            defaultDatePlaceholder: 'YYYY-MM-DD',
            //
            formErrorClass: 'form-error',
            FORMKEY: 'm__form',
            useNgFileUpload: true
        })
        //
        .constant('defaultFormElements', function () {
            return {
                'text': {element: 'input', type: 'text', editable: true, textBased: true},
                'date': {element: 'input', type: 'date', editable: true, textBased: true},
                'datetime': {element: 'input', type: 'datetime', editable: true, textBased: true},
                'datetime-local': {element: 'input', type: 'datetime-local', editable: true, textBased: true},
                'email': {element: 'input', type: 'email', editable: true, textBased: true},
                'month': {element: 'input', type: 'month', editable: true, textBased: true},
                'number': {element: 'input', type: 'number', editable: true, textBased: true},
                'password': {element: 'input', type: 'password', editable: true, textBased: true},
                'search': {element: 'input', type: 'search', editable: true, textBased: true},
                'tel': {element: 'input', type: 'tel', editable: true, textBased: true},
                'textarea': {element: 'textarea', editable: true, textBased: true},
                'time': {element: 'input', type: 'time', editable: true, textBased: true},
                'url': {element: 'input', type: 'url', editable: true, textBased: true},
                'week': {element: 'input', type: 'week', editable: true, textBased: true},
                //  Specialized editables
                'checkbox': {element: 'input', type: 'checkbox', editable: true, textBased: false},
                'color': {element: 'input', type: 'color', editable: true, textBased: false},
                'file': {element: 'input', type: 'file', editable: true, textBased: false},
                'range': {element: 'input', type: 'range', editable: true, textBased: false},
                'select': {element: 'select', editable: true, textBased: false},
                //  Pseudo-non-editables (containers)
                'checklist': {element: 'div', editable: false, textBased: false},
                'fieldset': {element: 'fieldset', editable: false, textBased: false},
                'div': {element: 'div', editable: false, textBased: false},
                'form': {element: 'form', editable: false, textBased: false},
                'radio': {element: 'div', editable: false, textBased: false},
                //  Non-editables (mostly buttons)
                'button': {element: 'button', type: 'button', editable: false, textBased: false},
                'hidden': {element: 'input', type: 'hidden', editable: false, textBased: false},
                'image': {element: 'input', type: 'image', editable: false, textBased: false},
                'legend': {element: 'legend', editable: false, textBased: false},
                'reset': {element: 'button', type: 'reset', editable: false, textBased: false},
                'submit': {element: 'button', type: 'submit', editable: false, textBased: false}
            };
        })
        //
        .factory('formElements', ['defaultFormElements', function (defaultFormElements) {
            return defaultFormElements;
        }])
        //
        .run(['$rootScope', '$lux', 'formDefaults',
            function (scope, $lux, formDefaults) {
                //
                //  Listen for a Lux form to be available
                //  If it uses the api for posting, register with it
                scope.$on('formReady', function (e, model, formScope) {
                    var attrs = formScope.formAttrs,
                        action = attrs ? attrs.action : null,
                        actionType = attrs ? attrs.actionType : null;

                    if (isObject(action) && actionType !== 'create') {
                        var api = $lux.api(action);
                        if (api) {
                            $lux.log.info('Form ' + formScope.formModelName + ' registered with "' +
                                api.toString() + '" api');
                            api.formReady(model, formScope);
                        }
                    }
                    //
                    // Convert date string to date object
                    lux.forms.directives.push(fieldToDate(formDefaults));
                });
            }]
        )
        //
        // A factory for rendering form fields
        .factory('baseForm', ['$log', '$http', '$document', '$templateCache',
            'formDefaults', 'formElements',
            function (log, $http, $document, $templateCache, formDefaults, formElements) {
                //
                var elements = formElements();

                return {
                    name: 'default',
                    //
                    elements: elements,
                    //
                    className: '',
                    //
                    inputGroupClass: 'form-group',
                    //
                    inputHiddenClass: 'form-hidden',
                    //
                    inputClass: 'form-control',
                    //
                    buttonClass: 'btn btn-default',
                    //
                    template: template,
                    //
                    // Create a form element
                    createElement: function (driver, scope) {

                        /**
                         * Builds infomation about type and text mode used in the field.
                         * These informations are used in `api.formReady` method.

                         * @param formModelName {string} - name of the model
                         * @param field {object}
                         * @param fieldType {string} - type of the field
                         */
                        function buildFieldInfo(formModelName, field, fieldType) {
                            var typeConfig = formModelName + 'Type';
                            var textMode = lux.getJsonOrNone(field.text_edit);
                            scope[typeConfig] = scope[typeConfig] || {};

                            if (textMode !== null)
                                scope[typeConfig][field.name] = textMode.mode || '';
                            else
                                scope[typeConfig][field.name] = fieldType;
                        }

                        var self = this,
                            thisField = scope.field,
                            tc = thisField.type.split('.'),
                            info = elements[tc.splice(0, 1)[0]],
                            renderer,
                            fieldType;

                        scope.extraClasses = tc.join(' ');
                        scope.info = info;

                        if (info) {
                            if (info.type && angular.isFunction(self[info.type]))
                            // Pick the renderer by checking `type`
                                fieldType = info.type;
                            else
                            // If no element type, use the `element`
                                fieldType = info.element;
                        }

                        renderer = self[fieldType];

                        buildFieldInfo(scope.formModelName, thisField, fieldType);

                        if (!renderer)
                            renderer = self.renderNotElements;

                        var element = renderer.call(self, scope);

                        forEach(scope.children, function (child) {
                            var field = child.field;

                            if (field) {

                                // extend child.field with options
                                forEach(formDefaults, function (_, name) {
                                    if (angular.isUndefined(field[name]))
                                        field[name] = scope.field[name];
                                });
                                //
                                // Make sure children is defined, otherwise it will be inherited from the parent scope
                                if (angular.isUndefined(child.children))
                                    child.children = null;
                                child = driver.createElement(extend(scope, child));

                                if (isArray(child))
                                    forEach(child, function (c) {
                                        element.append(c);
                                    });
                                else if (child)
                                    element.append(child);
                            } else {
                                log.error('form child without field');
                            }
                        });
                        // Reinstate the field
                        scope.field = thisField;
                        return element;
                    },
                    //
                    addAttrs: function (scope, element, attributes) {
                        forEach(scope.field, function (value, name) {
                            if (attributes.indexOf(name) > -1) {
                                if (ngAttributes.indexOf(name) > -1)
                                    element.attr('ng-' + name, value);
                                else
                                    element.attr(name, value);
                            } else if (name.substring(0, 5) === 'data-') {
                                element.attr(name, value);
                            }
                        });
                        return element;
                    },
                    //
                    renderNotForm: function (scope) {
                        var field = scope.field;
                        return angular.element($document[0].createElement('span')).html(field.label || '');
                    },
                    //
                    fillDefaults: function (scope) {
                        var field = scope.field;
                        field.label = field.label || field.name;
                        scope.formCount++;
                        if (!field.id)
                            field.id = field.name + '-' + scope.formid + '-' + scope.formCount;
                    },
                    //
                    form: function (scope) {
                        var field = scope.field,
                            info = scope.info,
                            form = angular.element($document[0].createElement(info.element))
                                .attr('role', 'form').addClass(this.className)
                                .attr('ng-model', field.model);
                        this.formMessages(scope, form);
                        return this.addAttrs(scope, form, formAttributes);
                    },
                    //
                    'ng-form': function (scope) {
                        return this.form(scope);
                    },
                    //
                    // Render a fieldset
                    fieldset: function (scope) {
                        var field = scope.field,
                            info = scope.info,
                            element = angular.element($document[0].createElement(info.element));
                        if (field.label)
                            element.append(angular.element($document[0].createElement('legend')).html(field.label));
                        return element;
                    },
                    //
                    div: function (scope) {
                        var info = scope.info,
                            element = angular.element($document[0].createElement(info.element)).addClass(scope.extraClasses);
                        return element;
                    },
                    //
                    radio: function (scope) {
                        this.fillDefaults(scope);

                        var field = scope.field,
                            info = scope.info,
                            input = angular.element($document[0].createElement(info.element)),
                            label = angular.element($document[0].createElement('label')).attr('for', field.id),
                            span = angular.element($document[0].createElement('span'))
                                .css('margin-left', '5px')
                                .css('position', 'relative')
                                .css('bottom', '2px')
                                .html(field.label),
                            element = angular.element($document[0].createElement('div')).addClass(this.element);

                        input.attr('ng-model', scope.formModelName + '["' + field.name + '"]');

                        forEach(inputAttributes, function (name) {
                            if (field[name]) input.attr(name, field[name]);
                        });

                        label.append(input).append(span);
                        element.append(label);
                        return this.onChange(scope, this.inputError(scope, element));
                    },
                    //
                    checkbox: function (scope) {
                        return this.radio(scope);
                    },
                    //
                    input: function (scope, attributes) {
                        this.fillDefaults(scope);

                        var field = scope.field,
                            info = scope.info,
                            input = angular.element($document[0].createElement(info.element)).addClass(this.inputClass),
                            label = angular.element($document[0].createElement('label')).attr('for', field.id).html(field.label),
                            modelOptions = angular.extend({}, field.modelOptions, scope.inputModelOptions),
                            element;

                        // Add model attribute
                        input.attr('ng-model', scope.formModelName + '["' + field.name + '"]');
                        // Add input model options
                        input.attr('ng-model-options', angular.toJson(modelOptions));

                        // Add default placeholder to date field if not exist
                        if (field.type === 'date' && angular.isUndefined(field.placeholder)) {
                            field.placeholder = formDefaults.defaultDatePlaceholder;
                        }

                        if (!field.showLabels || field.type === 'hidden') {
                            label.addClass('sr-only');
                            // Add placeholder if not defined
                            if (angular.isUndefined(field.placeholder))
                                field.placeholder = field.label;
                        }

                        this.addAttrs(scope, input, attributes || inputAttributes);
                        if (angular.isDefined(field.value)) {
                            scope[scope.formModelName][field.name] = field.value;
                            if (info.textBased)
                                input.attr('value', field.value);
                        }

                        // Add directive to element
                        input = addDirectives(scope, input);

                        if (this.inputGroupClass) {
                            element = angular.element($document[0].createElement('div'));
                            if (field.type === 'hidden') element.addClass(this.inputHiddenClass);
                            else element.addClass(this.inputGroupClass);
                            element.append(label).append(input);
                        } else {
                            element = [label, input];
                        }
                        return this.onChange(scope, this.inputError(scope, element));
                    },
                    //
                    textarea: function (scope) {
                        return this.input(scope, textareaAttributes);
                    },
                    //
                    // Create a select element
                    select: function (scope) {
                        var field = scope.field,
                            groups = {},
                            groupList = [],
                            options = [],
                            group;

                        forEach(field.options, function (opt) {
                            if (angular.isString(opt)) {
                                opt = {'value': opt};
                            } else if (isArray(opt)) {
                                opt = {
                                    'value': opt[0],
                                    'repr': opt[1] || opt[0]
                                };
                            }
                            if (opt.group) {
                                group = groups[opt.group];
                                if (!group) {
                                    group = {name: opt.group, options: []};
                                    groups[opt.group] = group;
                                    groupList.push(group);
                                }
                                group.options.push(opt);
                            } else
                                options.push(opt);
                            // Set the default value if not available
                            if (!field.value) field.value = opt.value;
                        });

                        var element = this.input(scope);

                        this.selectWidget(scope, element, field, groupList, options);

                        return this.onChange(scope, element);
                    },
                    //
                    // Standard select widget
                    selectWidget: function (scope, element, field, groupList, options) {
                        var grp,
                            placeholder,
                            select = _select(scope.info.element, element);

                        if (!field.multiple && angular.isUndefined(field['data-remote-options'])) {
                            placeholder = angular.element($document[0].createElement('option'))
                                .attr('value', '').text(field.placeholder || formDefaults.defaultSelectPlaceholder);

                            if (field.required) {
                                placeholder.prop('disabled', true);
                            }

                            select.append(placeholder);
                            if (angular.isUndefined(field.value)) {
                                field.value = '';
                            }
                        }

                        if (groupList.length) {
                            if (options.length)
                                groupList.push({name: 'other', options: options});

                            forEach(groupList, function (group) {
                                grp = angular.element($document[0].createElement('optgroup'))
                                    .attr('label', group.name);
                                select.append(grp);
                                forEach(group.options, function (opt) {
                                    opt = angular.element($document[0].createElement('option'))
                                        .attr('value', opt.value).html(opt.repr || opt.value);
                                    grp.append(opt);
                                });
                            });
                        } else {
                            forEach(options, function (opt) {
                                opt = angular.element($document[0].createElement('option'))
                                    .attr('value', opt.value).html(opt.repr || opt.value);
                                select.append(opt);
                            });
                        }

                        if (field.multiple)
                            select.attr('multiple', true);
                    },
                    //
                    button: function (scope) {
                        var field = scope.field,
                            info = scope.info,
                            element = angular.element($document[0].createElement(info.element)).addClass(this.buttonClass);
                        field.name = field.name || info.element;
                        field.label = field.label || field.name;
                        element.html(field.label);
                        this.addAttrs(scope, element, buttonAttributes);
                        return this.onClick(scope, element);
                    },
                    //
                    onClick: function (scope, element) {
                        var name = element.attr('name'),
                            field = scope.field,
                            clickname = name + 'Click',
                            self = this;
                        //
                        // scope function
                        scope[clickname] = function (e) {
                            if (scope.$broadcast(clickname, e).defaultPrevented) return;
                            if (scope.$emit(clickname, e).defaultPrevented) return;

                            // Get the form processing function
                            var callback = self.processForm(scope);
                            //
                            if (field.click) {
                                callback = lux.getObject(field, 'click', scope);
                                if (!angular.isFunction(callback)) {
                                    log.error('Could not locate click function "' + field.click + '" for button');
                                    return;
                                }
                            }
                            callback.call(this, e);
                        };
                        element.attr('ng-click', clickname + '($event)');
                        return element;
                    },
                    //
                    //  Add change event
                    onChange: function (scope, element) {
                        var field = scope.field,
                            input = angular.element(element[0].querySelector(scope.info.element));
                        input.attr('ng-change', 'fireFieldChange("' + field.name + '")');
                        return element;
                    },
                    //
                    // Add input error elements to the input element.
                    // Each input element may have one or more error handler depending
                    // on its type and attributes
                    inputError: function (scope, element) {
                        var field = scope.field,
                            self = this,
                        // True when the form is submitted
                            submitted = scope.formName + '.$submitted',
                        // True if the field is dirty
                            dirty = joinField(scope.formName, field.name, '$dirty'),
                            invalid = joinField(scope.formName, field.name, '$invalid'),
                            error = joinField(scope.formName, field.name, '$error') + '.',
                            input = angular.element(element[0].querySelector(scope.info.element)),
                            p = angular.element($document[0].createElement('p'))
                                .attr('ng-show', '(' + submitted + ' || ' + dirty + ') && ' + invalid)
                                .addClass('text-danger error-block')
                                .addClass(scope.formErrorClass),
                            value,
                            attrname;
                        // Loop through validation attributes
                        forEach(validationAttributes, function (attr) {
                            value = field[attr];
                            attrname = attr;
                            if (angular.isDefined(value) && value !== false && value !== null) {
                                if (ngAttributes.indexOf(attr) > -1) attrname = 'ng-' + attr;
                                input.attr(attrname, value);
                                p.append(angular.element($document[0].createElement('span'))
                                    .attr('ng-show', error + attr)
                                    .html(self.errorMessage(scope, attr)));
                            }
                        });

                        // Add the invalid handler if not available
                        var errors = p.children().length,
                            nameError = '$invalid';
                        if (errors)
                            nameError += ' && !' + joinField(scope.formName, field.name, '$error.required');
                        // Show only if server side errors don't exist
                        nameError += ' && !formErrors["' + field.name + '"]';
                        p.append(this.fieldErrorElement(scope, nameError, self.errorMessage(scope, 'invalid')));

                        // Add the invalid handler for server side errors
                        var name = '$invalid';
                        name += ' && !' + joinField(scope.formName, field.name, '$error.required');
                        // Show only if server side errors exists
                        name += ' && formErrors["' + field.name + '"]';
                        p.append(
                            this.fieldErrorElement(scope, name, self.errorMessage(scope, 'invalid'))
                                .html('{{formErrors["' + field.name + '"]}}')
                        );

                        return element.append(p);
                    },
                    //
                    fieldErrorElement: function (scope, name, msg) {
                        var field = scope.field,
                            value = joinField(scope.formName, field.name, name);

                        return angular.element($document[0].createElement('span'))
                            .attr('ng-show', value)
                            .html(msg);
                    },
                    //
                    // Add element which containes form messages and errors
                    formMessages: function (scope, form) {
                        var messages = angular.element($document[0].createElement('p')),
                            a = scope.formAttrs;
                        messages.attr('ng-repeat', 'message in formMessages.' + a.FORMKEY)
                            .attr('ng-bind', 'message.message')
                            .attr('ng-class', 'message.error ? "text-danger" : "text-info"');
                        return form.append(messages);
                    },
                    //
                    errorMessage: function (scope, attr) {
                        var message = attr + 'Message',
                            field = scope.field,
                            handler = this[attr + 'ErrorMessage'] || this.defaultErrorMesage;
                        return field[message] || handler.call(this, scope);
                    },
                    //
                    // Default error Message when the field is invalid
                    defaultErrorMesage: function (scope) {
                        var type = scope.field.type;
                        return 'Not a valid ' + type;
                    },
                    //
                    minErrorMessage: function (scope) {
                        return 'Must be greater than ' + scope.field.min;
                    },
                    //
                    maxErrorMessage: function (scope) {
                        return 'Must be less than ' + scope.field.max;
                    },
                    //
                    maxlengthErrorMessage: function (scope) {
                        return 'Too long, must be less than ' + scope.field.maxlength;
                    },
                    //
                    minlengthErrorMessage: function (scope) {
                        return 'Too short, must be more than ' + scope.field.minlength;
                    },
                    //
                    requiredErrorMessage: function (scope) {
                        var msg = scope.field.required_error;
                        return msg || scope.field.label + ' is required';
                    },
                    //
                    // Return the function to handle form processing
                    processForm: function (scope) {
                        return scope.processForm || lux.processForm;
                    }
                };

                function template (url) {
                    return $http.get(url, {cache: $templateCache}).then(function (result) {
                        return result.data;
                    });
                }

                function _select(tag, element) {
                    if (isArray(element)) {
                        for (var i = 0; i < element.length; ++i) {
                            if (element[0].tagName === tag)
                                return element;
                        }
                    } else {
                        return angular.element(element[0].querySelector(tag));
                    }
                }
            }
        ])
        //
        .factory('standardForm', ['baseForm', function (baseForm) {
            return extendForm(baseForm);
        }])
        //
        // Bootstrap Horizontal form renderer
        .factory('horizontalForm', ['$document', 'baseForm', function ($document, baseForm) {
            //
            // extend the standardForm factory
            var baseInput = baseForm.input,
                baseButton = baseForm.button,
                form = extendForm(baseForm, {
                    name: 'horizontal',
                    className: 'form-horizontal',
                    input: input,
                    button: button
                });

            return form;

            function input (scope) {
                var element = baseInput(scope),
                    children = element.children(),
                    labelSpan = scope.field.labelSpan ? +scope.field.labelSpan : 2,
                    wrapper = angular.element($document[0].createElement('div'));
                labelSpan = Math.max(2, Math.min(labelSpan, 10));
                angular.element(children[0]).addClass('control-label col-sm-' + labelSpan);
                wrapper.addClass('col-sm-' + (12-labelSpan));
                for (var i=1; i<children.length; ++i)
                    wrapper.append(angular.element(children[i]));
                return element.append(wrapper);
            }

            function button (scope) {
                var element = baseButton(scope),
                    labelSpan = scope.field.labelSpan ? +scope.field.labelSpan : 2,
                    outer = angular.element($document[0].createElement('div')).addClass(form.inputGroupClass),
                    wrapper = angular.element($document[0].createElement('div'));
                labelSpan = Math.max(2, Math.min(labelSpan, 10));
                wrapper.addClass('col-sm-offset-' + labelSpan)
                       .addClass('col-sm-' + (12-labelSpan));
                outer.append(wrapper.append(element));
                return outer;
            }
        }])
        //
        .factory('inlineForm', ['baseForm', function (baseForm) {
            var baseInput = baseForm.input;

            return extendForm(baseForm, {
                name: 'inline',
                className: 'form-inline',
                input: input
            });

            function input (scope) {
                var element = baseInput(scope);
                angular.element(element[0].getElementsByTagName('label')).addClass('sr-only');
                return element;
            }
        }])
        //
        .factory('formRenderer', ['$lux', '$compile', 'formDefaults',
            'standardForm', 'horizontalForm', 'inlineForm',
            function ($lux, $compile, formDefaults, standardForm, horizontalForm, inlineForm) {
                //
                function renderer(scope, element, attrs) {
                    var data = lux.getOptions(attrs);

                    // No data, maybe this form was loaded via angular ui router
                    // try to evaluate internal scripts
                    if (!data) {
                        var scripts = element[0].getElementsByTagName('script');
                        angular.forEach(scripts, function (js) {
                            lux.globalEval(js.innerHTML);
                        });
                        data = lux.getOptions(attrs);
                    }

                    if (data && data.field) {
                        var form = data.field,
                            formmodel = {};

                        // extend with form defaults
                        data.field = extend({}, formDefaults, form);
                        extend(scope, data);
                        form = scope.field;
                        if (form.model) {
                            if (!form.name)
                                form.name = form.model + 'form';
                            scope.$parent[form.model] = formmodel;
                        } else {
                            if (!form.name)
                                form.name = 'form';
                            form.model = form.name + 'Model';
                        }
                        scope.formName = form.name;
                        scope.formModelName = form.model;
                        //
                        scope[scope.formModelName] = formmodel;
                        scope.formAttrs = form;
                        scope.formClasses = {};
                        scope.formErrors = {};
                        scope.formMessages = {};
                        scope.inputModelOptions = {
                            debounce: formDefaults.debounce
                        };
                        scope.$lux = $lux;
                        if (!form.id)
                            form.id = formid();
                        scope.formid = form.id;
                        scope.formCount = 0;

                        scope.addMessages = function (messages, error) {

                            forEach(messages, function (message) {
                                if (isString(message))
                                    message = {message: message};

                                var field = message.field;
                                if (field && !scope[scope.formName].hasOwnProperty(field)) {
                                    message.message = field + ' ' + message.message;
                                    field = formDefaults.FORMKEY;
                                } else if (!field) {
                                    field = formDefaults.FORMKEY;
                                }

                                if (error) message.error = error;

                                scope.formMessages[field] = [message];

                                if (message.error && field !== formDefaults.FORMKEY) {
                                    scope.formErrors[field] = message.message;
                                    scope[scope.formName][field].$invalid = true;
                                }
                            });
                        };

                        scope.fireFieldChange = function (field) {
                            // Delete previous field error from server side
                            if (angular.isDefined(scope.formErrors[field])) {
                                delete scope.formErrors[field];
                            }
                            // Triggered every time a form field changes
                            scope.$broadcast('fieldChange', formmodel, field);
                            scope.$emit('formFieldChange', formmodel, field);
                        };
                    } else {
                        $lux.log.error('Form data does not contain field entry');
                    }
                }

                //
                renderer.createForm = function (scope, element) {
                    var form = scope.field;
                    if (form) {
                        var formElement = renderer.createElement(scope);
                        //  Compile and update DOM
                        if (formElement) {
                            renderer.preCompile(scope, formElement);
                            $compile(formElement)(scope);
                            element.replaceWith(formElement);
                            renderer.postCompile(scope, formElement);
                        }
                    }
                };

                renderer.createElement = function (scope) {
                    var field = scope.field;

                    if (this[field.layout])
                        return this[field.layout].createElement(this, scope);
                    else
                        $lux.log.error('Layout "' + field.layout + '" not available, cannot render form');
                };

                renderer.preCompile = function () {
                };

                renderer.postCompile = function () {
                };

                renderer.checkField = function (name) {
                    var checker = this['check_' + name];
                    // There may be a custom field checker
                    if (checker)
                        checker.call(this);
                    else {
                        var field = this.form[name];
                        if (field.$valid)
                            this.formClasses[name] = 'has-success';
                        else if (field.$dirty) {
                            this.formErrors[name] = name + ' is not valid';
                            this.formClasses[name] = 'has-error';
                        }
                    }
                };

                renderer.processForm = function (scope) {
                    // Clear form errors and messages
                    scope.formMessages = [];
                    scope.formErrors = [];

                    if (scope.form.$invalid) {
                        return scope.showErrors();
                    }
                };

                // Create the directive
                renderer[standardForm.name] = standardForm;

                renderer[horizontalForm.name] = horizontalForm;

                renderer[inlineForm.name] = inlineForm;

                return renderer;
            }
        ])
        //
        // Lux form
        .directive('luxForm', ['formRenderer', function (formRenderer) {
            return {
                restrict: 'AE',
                //
                scope: {},
                //
                compile: function () {
                    return {
                        pre: function (scope, element, attr) {
                            // Initialise the scope from the attributes
                            formRenderer(scope, element, attr);
                        },
                        post: function (scope, element) {
                            // create the form
                            formRenderer.createForm(scope, element);
                            // Emit the form upwards through the scope hierarchy
                            scope.$emit('formReady', scope[scope.formModelName], scope);
                        }
                    };
                }
            };
        }])
        //
        // A directive which add keyup and change event callaback
        .directive('watchChange', [function() {
            return {
                scope: {
                    onchange: '&watchChange'
                },
                //
                link: function(scope, element) {
                    element.on('keyup', function() {
                        scope.$apply(function () {
                            scope.onchange();
                        });
                    }).on('change', function() {
                        scope.$apply(function () {
                            scope.onchange();
                        });
                    });
                }
            };
        }])
        //
        // Format string date to date object
        .directive('formatDate', [function () {
            return {
                require: '?ngModel',
                link: function (scope, elem, attrs, ngModel) {
                    // All date-related inputs like <input type='date'>
                    // require the model to be a Date object in Angular 1.3+.
                    ngModel.$formatters.push(function(modelValue){
                        if (angular.isString(modelValue) || angular.isNumber(modelValue))
                            return new Date(modelValue);
                        return modelValue;
                    });
                }
            };
        }]);

    return lux;

    function joinField(model, name, extra) {
        return model + '["' + name + '"].' + extra;
    }

    function fieldToDate(formDefaults) {

        return convert;

        function convert(scope, element) {
            if (formDefaults.dateTypes.indexOf(scope.field.type) > -1)
                element.attr('format-date', '');
        }
    }

    function addDirectives(scope, element) {
        angular.forEach(lux.forms.directives, function (callback) {
            callback(scope, element);
        });
        return element;
    }
});
