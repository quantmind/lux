    var FORMKEY = 'm__form',
        formDefaults = {};
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
        $scope.processForm = function($event) {
            $event.preventDefault();
            $event.stopPropagation();
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
    };

    var input_attributes = ['id', 'class', 'form', 'max', 'maxlength',
                            'min', 'name', 'placeholder', 'readonly',
                            'required', 'style', 'title', 'type', 'value'],
        form_attributes = ['id', 'class', 'style', 'title',
                           'action', 'enctype', 'name', 'novalidate'],
        global_attributes = ['id', 'class', 'style', 'title'],
        form_inputs = ['button', 'checkbox', 'color', 'date', 'datetime',
                       'datetime-local', 'email', 'file', 'hidden', 'image',
                       'month', 'number', 'password', 'radio', 'range',
                       'reset', 'search', 'submit', 'tel', 'text', 'time',
                       'url', 'week'];


    // Default form module for lux
    angular.module('lux.form', ['lux.services'])
        .value('elementAttributes', function (type) {
            if (form_inputs.indexOf(type) > -1)
                return input_attributes;
            else if (type === 'form')
                return form_attributes;
            else
                return global_attributes;
        })
        //
        // The formService is a reusable component for redering form fields
        .service('formService', ['$compile', '$log', 'elementAttributes',
                function ($compile, log, elementAttributes) {

            var radioTemplate = '<label>'+
                                '<input ng-class="field.class" ng-model="form[field.name]" id="{{field.id}}" name="{{field.name}}">'+
                                ' {{field.label}}</label>',
                inputTemplate = '<div class="form-group">'+
                                '<label for="{{field.id}}"> {{field.label}}</label>'+
                                '<input ng-class="field.class" ng-model="form[field.name]" id="{{field.id}}" name="{{field.name}}">'+
                                '</div>',
                fieldsetTemplate = '<fieldset><legend ng-if="field.legend">{{field.legend}}</legend></fieldset>';

            function fillDefaults (scope) {
                var field = scope.field;
                field.label = field.label || field.name;
                scope.formParameters[field.name] = 'form.' + field.name;
                scope.count++;
                if (!field.id)
                    field.id = field.name + '-' + scope.formid + '-' + scope.count;
            }

            // add attributes ``attrs`` to ``element``
            this.attrs = function (scope, element) {
                var attributes = elementAttributes(scope.field.type);
                forEach(scope.field, function (value, name) {
                    if (attributes.indexOf(name) > -1)
                        element.attr(name, value);
                });
                return element;
            };

            // Clear parent attributes
            this.removeAttrs = function (scope, element) {
                var attributes = elementAttributes(scope.type);
                forEach(attributes, function (name) {
                    delete scope[name];
                });
            };

            // Compile a form element with a scope
            this.compile = function (scope, element) {
                var self = this,
                    attributes = elementAttributes(scope.field.type);


                forEach(scope.children, function (child) {

                    if (child.field) {

                        var childScope = scope.$new(),
                            fieldCompiler = self[child.field.type];

                        // extend child.field with options
                        forEach(scope.field, function (value, name) {
                            if (attributes.indexOf(name) === -1 && child.field[name] === undefined)
                                child.field[name] = value;
                        });

                        if (!fieldCompiler)
                            fieldCompiler = self.input;

                        // extend child scope options with values form child attributes
                        element.append(fieldCompiler.call(self, extend(childScope, child)));
                    } else {
                        log.error('form child without field');
                    }
                });

                return this.attrs(scope, element);
            };

            // Compile a fieldset and its children
            this.fieldset = function (scope) {
                var element = $compile(fieldsetTemplate)(scope);
                return this.compile(scope, element);
            };

            this.radio = function (scope) {
                fillDefaults(scope);
                return this.attrs(scope, $compile(radioTemplate)(scope));
            };
            this.checkbox = this.radio;

            this.input = function (scope) {
                fillDefaults(scope);
                if (!scope.field.class)
                    scope.field.class = 'form-control';
                return $compile(inputTemplate)(scope);
                //return this.attrs(scope, $compile(inputTemplate)(scope));
            };

            this.button = function (scope) {
                var field = scope.field;
                if (field.click) {
                    field.ngclick = function (e) {
                        //
                    };
                }
                return $compile('<button ng-click="field.ngclick">{{field.name}}</button>')(scope);
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

        }])
        //
        // Default Lux form
        .directive('luxForm', ['$log', 'formService', function (log, formService) {

            return {
                restrict: "AE",
                //
                link: function (scope, element, attrs) {
                    // Initialise the scope from the attributes
                    var form = extend({}, formDefaults, getOptions(attrs));
                    if (form.field) {
                        element.html('');
                        // Form has a type (the tag), create the form element
                        if (form.field.type) {
                            var el = angular.element('<' + form.field.type + '>').attr('role', 'form');
                            element.append(el);
                            element = el;
                        }
                        extend(scope, form);
                        scope.form = {};
                        scope.formParameters = {};
                        scope.formid = scope.id;
                        scope.count = 0;
                        if (!scope.formid)
                            scope.formid = 'f' + s4();
                        formService.compile(scope, element);
                    } else {
                        log.error('Form data does not contain field entry');
                    }
                }
            };
        }])
        //
        // Controller for a field in a Form with default layout
        .controller('FormField', ['$scope', 'formService', function (scope, formService) {
            var field = scope.field;
            if (field.type === 'checkbox' || field.type === 'radio') {
                field.radio = true;
                field.groupClass = field.type;
            }
            else
                field.groupClass = 'form-group';
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
        })
        //
        .directive('luxInput', function($parse) {
            return {
                restrict: "A",
                compile: function($element, $attrs) {
                    var initialValue = $attrs.value || $element.val();
                    if (initialValue) {
                        return {
                            pre: function($scope, $element, $attrs) {
                                $parse($attrs.ngModel).assign($scope, initialValue);
                                $scope.$apply();
                            }
                        };
                    }
                }
            };
        });
