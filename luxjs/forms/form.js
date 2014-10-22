    var FORMKEY = 'm__form',
        formDefaults = {
            layout: 'default',
            // for horizontal layout
            labelSpan: 2,
            showLabels: true,
            novalidate: true
        };
    //
    // Change the form data depending on content type
    function formData(ct) {

        return function (data, getHeaders ) {
            angular.extend(data, lux.context.csrf);
            if (ct === 'application/x-www-form-urlencoded')
                return $.param(data);
            else if (ct === 'multipart/form-data') {
                var fd = new FormData();
                angular.forEach(data, function (value, key) {
                    fd.append(key, value);
                });
                return fd;
            } else {
                return data;
            }
        };
    }

    lux.processForm = function (e) {
        e.preventDefault();
        e.stopPropagation();
        var form = this[this.formName];

        var $element = angular.element($event.target),
            apiname = $element.attr('data-api'),
            target = $element.attr('action'),
            promise,
            api;
        //
        if ($scope.form.$invalid) {
            return $scope.showErrors();
        }

        // Get the api information
        if (!target && apiname) {
            api = $lux.api(apiname);
            if (!api)
                $lux.log.error('Could not find api url for ' + apiname);
        }

        $scope.formMessages = {};
        //
        if (target) {
            var enctype = $element.attr('enctype') || '',
                ct = enctype.split(';')[0],
                options = {
                    url: target,
                    method: $element.attr('method') || 'POST',
                    data: $scope.formModel,
                    transformRequest: formData(ct),
                };
            // Let the browser choose the content type
            if (ct === 'application/x-www-form-urlencoded' || ct === 'multipart/form-data') {
                options.headers = {
                    'content-type': undefined
                };
            }
            promise = $lux.http(options);
        } else if (api) {
            promise = api.put($scope.formModel);
        } else {
            $lux.log.error('Could not process form. No target or api');
            return;
        }
        //
        promise.success(function(data, status) {
            if (data.messages) {
                angular.forEach(data.messages, function (messages, field) {
                    $scope.formMessages[field] = messages;
                });
            } else if (api) {
                // Created
                if (status === 201) {
                    $scope.formMessages[FORMKEY] = [{message: 'Succesfully created'}];
                } else {
                    $scope.formMessages[FORMKEY] = [{message: 'Succesfully updated'}];
                }
            } else {
                window.location.href = data.redirect || '/';
            }
        }).error(function(data, status, headers) {
            var messages, msg;
            if (data) {
                messages = data.messages;
                if (!messages) {
                    msg = data.message;
                    if (!msg) {
                        status = status || data.status || 501;
                        msg = 'Server error (' + data.status + ')';
                    }
                    messages = {};
                    messages[FORMKEY] = [{message: msg, error: true}];
                }
            } else {
                status = status || 501;
                msg = 'Server error (' + data.status + ')';
                messages = {};
                messages[FORMKEY] = [{message: msg, error: true}];
            }
            formMessages(messages);
        });
    };

    // A general from controller factory
    var formController = lux.formController = function ($scope, $lux, model) {
        model || (model = {});

        var page = $scope.$parent ? $scope.$parent.page : {};

        if (model)
            $scope.formModel = model.data || model;
        $scope.formClasses = {};
        $scope.formErrors = {};
        $scope.formMessages = {};

        if ($scope.formModel.name) {
            page.title = 'Update ' + $scope.formModel.name;
        }

        function formMessages (messages) {
            angular.forEach(messages, function (messages, field) {
                $scope.formMessages[field] = messages;
            });
        }

        // display field errors
        $scope.showErrors = function () {
            var error = $scope.form.$error;
            angular.forEach(error.required, function (e) {
                $scope.formClasses[e.$name] = 'has-error';
            });
        };

        // process form
        $scope.processForm = lux.processForm;
    };


    // Default form module for lux
    angular.module('lux.form', ['lux.services'])
        //
        // The formService is a reusable component for redering form fields
        .service('standardForm', ['$log', '$http', '$document', '$templateCache',
                function (log, $http, $document, $templateCache) {

            var supported = {
                    //  Text-based elements
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
                    'form': {element: 'form', editable: false, textBased: false},
                    'radio': {element: 'div', editable: false, textBased: false},
                    //  Non-editables (mostly buttons)
                    'button': {element: 'button', type: 'button', editable: false, textBased: false},
                    'hidden': {element: 'input', type: 'hidden', editable: false, textBased: false},
                    'image': {element: 'input', type: 'image', editable: false, textBased: false},
                    'legend': {element: 'legend', editable: false, textBased: false},
                    'reset': {element: 'button', type: 'reset', editable: false, textBased: false},
                    'submit': {element: 'button', type: 'submit', editable: false, textBased: false}
                },
                //
                baseAttributes = ['id', 'name', 'title', 'style'],
                inputAttributes = extendArray([], baseAttributes, ['disabled', 'type', 'value', 'placeholder']),
                buttonAttributes = extendArray([], baseAttributes, ['disabled']),
                formAttributes = extendArray([], baseAttributes, ['accept-charset', 'action', 'autocomplete',
                                                                  'enctype', 'method', 'novalidate', 'target']),
                validationAttributes = ['minlength', 'maxlength', 'min', 'max', 'required'],
                ngAttributes = ['disabled', 'minlength', 'maxlength', 'required'];

            extend(this, {
                name: 'default',
                //
                className: '',
                //
                inputGroupClass: 'form-group',
                //
                inputClass: 'form-control',
                //
                buttonClass: 'btn btn-default',
                //
                template: function (url) {
                    return $http.get(url, {cache: $templateCache}).then(function (result) {
                        return result.data;
                    });
                },
                //
                createElement: function (driver, scope) {
                    var self = this,
                        field = scope.field,
                        info = supported[field.type],
                        renderer;

                    scope.info = info;

                    if (info)
                        renderer = this[info.element];

                    if (!renderer)
                        renderer = this.renderNotSupported;

                    var element = renderer.call(this, scope);

                    forEach(scope.children, function (child) {
                        field = child.field;

                        if (field) {

                            // extend child.field with options
                            forEach(formDefaults, function (_, name) {
                                if (field[name] === undefined)
                                    field[name] = scope.field[name];
                            });
                            //
                            // Make sure children is defined, otherwise it will be inherited from the parent scope
                            if (child.children === undefined)
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
                    extend(scope, field);
                    return element;
                },
                //
                addAttrs: function (scope, element, attributes) {
                    var field = scope.field,
                        value;
                    forEach(attributes, function (name) {
                        value = field[name];
                        if (value !== undefined && value !== false) {
                            if (ngAttributes.indexOf(name) > -1)
                                element.attr('ng-' + name, value);
                            else {
                                if (value === true) value = '';
                                element.attr(name, value);
                            }
                        }
                    });
                    return element;
                },
                //
                renderNotSupported: function (scope) {
                    return $($document[0].createElement('span')).html(field.label || '');
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
                        form = $($document[0].createElement(info.element))
                                    .attr('role', 'form').addClass(this.className)
                                    .attr('ng-model', field.model);
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
                        element = $($document[0].createElement(info.element));
                    if (field.label)
                        element.append($($document[0].createElement('legend')).html(field.label));
                    return element;
                },
                //
                radio: function (scope) {
                    this.fillDefaults(scope);

                    var field = scope.field,
                        info = scope.info,
                        input = angular.element($document[0].createElement(info.element)).addClass(this.inputClass),
                        label = angular.element($document[0].createElement('label')),
                        element = angular.element($document[0].createElement('div')).addClass(this.element);

                    input.attr('ng-model', scope.formModelName + '.' + field.name);

                    forEach(InputAttributes, function (name) {
                        if (field[name]) input.attr(name, field[name]);
                    });

                    return element.append(label.append(input));
                },
                //
                checkbox: function (scope) {
                    return this.radio(scope);
                },
                //
                input: function (scope) {
                    this.fillDefaults(scope);

                    var field = scope.field,
                        info = scope.info,
                        input = angular.element($document[0].createElement(info.element)).addClass(this.inputClass),
                        label = angular.element($document[0].createElement('label')).attr('for', field.id).html(field.label),
                        element;

                    input.attr('ng-model', scope.formModelName + '.' + field.name);
                    this.addAttrs(scope, input, inputAttributes);

                    if (!field.showLabels)
                        label.addClass('sr-only');

                    if (field.value !== undefined) {
                        scope[scope.formModelName][field.name] = field.value;
                        if (info.textBased)
                            input.attr('value', field.value);
                    }

                    if (this.inputGroupClass) {
                        element = angular.element($document[0].createElement('div')).addClass(this.inputGroupClass);
                        element.append(label).append(input);
                    } else {
                        element = [label, input];
                    }
                    return this.inputError(scope, element);
                },
                //
                textarea: function (scope) {
                    return this.input(scope);
                },
                //
                // Create a select element
                select: function (scope) {
                    var field = scope.field,
                        info = scope.info,
                        element = this.input(scope),
                        select = this._select(info.element, element);
                    forEach(field.options, function (opt) {
                        if (typeof(opt) === 'string') {
                            opt = {'value': opt};
                        }
                        opt = $($document[0].createElement('option'))
                                .attr('value', opt.value).html(opt.repr || opt.value);
                        select.append(opt);
                    });
                    return element;
                },
                //
                button: function (scope) {
                    var field = scope.field,
                        info = scope.info,
                        element = $($document[0].createElement(info.element)).addClass(this.buttonClass);
                    if (!field.name)
                        field.name = field.label || info.element;
                    field.label = field.label || field.name;
                    element.html(field.label);
                    this.addAttrs(scope, element, buttonAttributes);
                    return this.onClick(scope, element);
                },
                //
                onClick: function (scope, element) {
                    if (scope.field.click) {
                        var name = element.attr('name'),
                            clickname = name + 'Click';
                        //
                        // scope function
                        scope[clickname] = function (e) {
                            var callback = getRootAttribute(this.field.click);
                            if (angular.isFunction(callback)) {
                                callback.call(this, e);
                            } else
                                log.error('Could not locate click function "' + field.click + '" for button');
                        };
                        element.attr('ng-click', clickname + '($event)');
                    }
                    return element;
                },
                //
                inputError: function (scope, element) {
                    var field = scope.field,
                        self = this,
                        dirty = [scope.formName, field.name, '$dirty'].join('.'),
                        invalid = [scope.formName, field.name, '$invalid'].join('.'),
                        error = [scope.formName, field.name, '$error'].join('.') + '.',
                        input = $(element[0].querySelector(scope.info.element)),
                        p = $($document[0].createElement('p'))
                                .attr('ng-show', dirty + ' && ' + invalid)
                                .addClass('text-danger form-error')
                                .html('{{formErrors.' + field.name + '}}'),
                        value,
                        attrname;
                    forEach(validationAttributes, function (attr) {
                        value = field[attr];
                        attrname = attr;
                        if (value !== undefined && value !== false && value !== null) {
                            if (ngAttributes.indexOf(attr) > -1) attrname = 'ng-' + attr;
                            input.attr(attrname, value);
                            p.append($($document[0].createElement('span'))
                                         .attr('ng-show', error + attr)
                                         .html(self.errorMessage(scope, attr)));
                        }
                    });
                    return element.append(p);
                },
                //
                errorMessage: function (scope, attr) {
                    var message = attr + 'Message',
                        field = scope.field,
                        handler = this[attr+'ErrorMessage'] || this.defaultErrorMesage;
                    return field[message] || handler.call(this, scope);
                },
                //
                defaultErrorMesage: function (scope) {
                    return 'Not a valid value';
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
                requiredErrorMessage: function (scope) {
                    return "This field is required";
                },
                //
                _select: function (tag, element) {
                    if (isArray(element)) {
                        for (var i=0; i<element.length; ++i) {
                            if (element[0].tagName === tag)
                                return element;
                        }
                    } else {
                        return $(element[0].querySelector(tag));
                    }
                }
            });
        }])
        //
        // Bootstrap Horizontal form renderer
        .service('horizontalForm', ['$document', 'standardForm', function ($document, standardForm) {
            //
            // extend the standardForm service
            extend(this, standardForm, {

                name: 'horizontal',

                className: 'form-horizontal',

                input: function (scope) {
                    var element = standardForm.input(scope),
                        children = element.children(),
                        labelSpan = scope.field.labelSpan ? +scope.field.labelSpan : 2,
                        wrapper = $($document[0].createElement('div'));
                    labelSpan = Math.max(2, Math.min(labelSpan, 10));
                    $(children[0]).addClass('control-label col-sm-' + labelSpan);
                    wrapper.addClass('col-sm-' + (12-labelSpan));
                    for (var i=1; i<children.length; ++i)
                        wrapper.append($(children[i]));
                    return element.append(wrapper);
                },

                button: function (scope) {
                    var element = standardForm.button(scope),
                        labelSpan = scope.field.labelSpan ? +scope.field.labelSpan : 2,
                        outer = $($document[0].createElement('div')).addClass(this.inputGroupClass),
                        wrapper = $($document[0].createElement('div'));
                    labelSpan = Math.max(2, Math.min(labelSpan, 10));
                    wrapper.addClass('col-sm-offset-' + labelSpan)
                           .addClass('col-sm-' + (12-labelSpan));
                    outer.append(wrapper.append(element));
                    return outer;
                }
            });
        }])
        //
        .service('inlineForm', ['standardForm', function (standardForm) {
            extend(this, standardForm, {
                name: 'inline',
                inputTemplateUrl: "forms/inlineInput.tpl.html",
                checkTemplateUrl: "forms/inlineCheck.tpl.html"
            });
        }])
        //
        .service('formBaseRenderer', ['$log', '$compile', function (log, $compile) {
            //
            // Internal function for compiling a scope
            this.createElement = function (scope) {
                var field = scope.field;

                if (this[field.layout])
                    return this[field.layout].createElement(this, scope);
                else
                    log.error('Layout "' + field.layout + '" not available, cannot render form');
            };
            //
            this.createForm = function (scope, element, attrs) {
                var data = getOptions(attrs),
                    form = data.field;
                if (form) {
                    // extend with form defaults
                    data.field = extend({}, formDefaults, form);
                    extend(scope, data);
                    form = scope.field;
                    if (!form.name)
                        form.name = 'form';
                    form.model = form.model ? form.model : form.name;
                    if (form.model === form.name)
                        form.model = form.model + 'Model';
                    scope.formName = form.name;
                    scope.formModelName = form.model;
                    //
                    scope[scope.formModelName] = {};
                    scope.formClasses = {};
                    scope.formErrors = {};
                    scope.formMessages = {};
                    if (!form.id)
                        form.id = 'f' + s4();
                    scope.formid = form.id;
                    scope.formCount = 0;
                    form = this.createElement(scope);

                    //  Compile and update DOM
                    if (form) {
                        $compile(form)(scope);
                        element.replaceWith(form);
                    }
                } else {
                    log.error('Form data does not contain field entry');
                }
            };

            this.checkField = function (name) {
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

            this.processForm = function(scope) {
                //
                if (scope.form.$invalid) {
                    return $scope.showErrors();
                }
            };
        }])
        //
        // Default form Renderer, roll your own if you like
        .service('formRenderer', ['formBaseRenderer', 'standardForm', 'horizontalForm', 'inlineForm',
            function (base, stdForm, horForm, inlForm) {
                extend(this, base);
                this[stdForm.name] = stdForm;
                this[horForm.name] = horForm;
                this[inlForm.name] = inlForm;
        }])
        //
        // Lux form
        .directive('luxForm', ['formRenderer', function (renderer) {

            return {
                restrict: "AE",
                //
                scope: {},
                //
                link: function (scope, element, attrs) {
                    // Initialise the scope from the attributes
                    renderer.createForm(scope, element, attrs);
                }
            };
        }])
        //
        // A directive which add keyup and change event callaback
        .directive('watchChange', function() {
            return {
                scope: {
                    onchange: '&watchChange'
                },
                //
                link: function(scope, element, attrs) {
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
        });
