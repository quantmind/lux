    //
    // Directive allows to add CodeMirror to the textarea elements
    //  ============================
    //
    angular.module('lux.codemirror', ['lux.services'])
        .constant('luxCodemirrorDefaults', {
            lineWrapping : true,
            lineNumbers: true,
            mode: lux.context.CODEMIRROR_MODE || "markdown",
            theme: lux.context.CODEMIRROR_THEME || "monokai",
        })
        .directive('luxCodemirror', ['$rootScope', '$lux', 'luxCodemirrorDefaults', function ($rootScope, $lux, luxCodemirrorDefaults) {
            //
            function initCodemirror() {
                loadCss('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.3.0/codemirror.css');
                loadCss('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.3.0/theme/' + luxCodemirrorDefaults.theme + '.css');
            }
            //
            function newEditor(element, options) {
                var codemirror;

                if (element[0].tagName === 'TEXTAREA') {
                    codemirror = window.CodeMirror.fromTextArea(element[0], options);
                } else {
                    element.html('');
                    codemirror = new window.CodeMirror(function(cm_el) {
                        element.append(cm_el);
                    }, options);
                }

                return codemirror;
            }
            //
            function optionsWatcher(codemirror, codemirrorAttr, scope) {
                if (!codemirrorAttr) return;

                var codemirrorDefaultsKeys = Object.keys(window.CodeMirror.defaults);
                scope.$watch(codemirrorAttr, updateOptions, true);

                function updateOptions(newValues, oldValue) {
                    if (!angular.isObject(newValues)) return;

                    codemirrorDefaultsKeys.forEach(function(key) {
                        if (newValues.hasOwnProperty(key)) {

                            if (oldValue && newValues[key] === oldValue[key])
                                return;

                        codemirror.setOption(key, newValues[key]);
                        }
                    });
                }
            }
            //
            function ngModelLink(codemirror, ngModel, scope) {
                if (!ngModel) return;

                // CodeMirror expects a string, so make sure it gets one.
                // This does not change the model.
                ngModel.$formatters.push(function(value) {
                    if (angular.isUndefined(value) || value === null)
                        return '';
                    else if (angular.isObject(value) || angular.isArray(value))
                        throw new Error('codemirror cannot use an object or an array as a model');
                    return value;
                });

                // Override the ngModelController $render method, which is what gets called when the model is updated.
                // This takes care of the synchronizing the codeMirror element with the underlying model, in the case that it is changed by something else.
                ngModel.$render = function() {
                    var safeViewValue = ngModel.$viewValue || '';
                    codemirror.setValue(safeViewValue);
                };

                // Keep the ngModel in sync with changes from CodeMirror
                codemirror.on('change', function(instance) {
                    var newValue = instance.getValue();
                    if (newValue !== ngModel.$viewValue) {
                        scope.$evalAsync(function() {
                            ngModel.$setViewValue(newValue);
                        });
                    }
                });
            }
            //
            function refreshAttribute(codemirror, refreshAttr, scope) {
                if (!refreshAttr) return;

                scope.$watch(refreshAttr, function(newVal, oldVal) {
                    // Skip the initial watch firing
                    if (newVal !== oldVal) {
                        $timeout(function() {
                            codemirror.refresh();
                        });
                    }
                });
            }
            //
            return {
                restrict: 'EA',
                require: '?ngModel',
                //
                compile: function () {
                    // Require CodeMirror
                    if (angular.isUndefined(window.CodeMirror)) {
                        throw new Error('lux-codemirror needs CodeMirror to work!');
                    }

                    initCodemirror();

                    return {
                        post: function(scope, element, attrs, ngModel) {

                            var options = angular.extend(
                                { value: element.text() },
                                luxCodemirrorDefaults || {},
                                scope.$eval(attrs.luxCodemirrorOpts)
                            );

                            var codemirror = newEditor(element, options);

                            optionsWatcher(
                                codemirror,
                                attrs.luxCodemirrorOpts,
                                scope
                            );

                            ngModelLink(codemirror, ngModel, scope);

                            refreshAttribute(codemirror, attrs.refresh, scope);

                            // Allow access to the CodeMirror instance through a broadcasted event
                            // eg: $broadcast('CodeMirror', function(cm){...});
                            scope.$on('CodeMirror', function(event, callback) {
                                if (angular.isFunction(callback))
                                    callback(codemirror);
                                else
                                    throw new Error('the CodeMirror event requires a callback function');
                            });

                            $rootScope.$on('$viewContentLoaded', function () {
                                codemirror.refresh();
                            });
                        }
                    };
                }
            };
        }]);
