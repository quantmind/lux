    //
    //  Lux Codemirror module
    //  ============================
    //  Directive allows to add CodeMirror to the textarea elements
    //
    //  Html:
    //
    //      <textarea lux-codemirror="{'mode': 'html'}"></div>
    //
    //
    //  Supported modes:
    //
    //      html, markdown, json
    //
    //
    //  ============================
    //
    angular.module('lux.codemirror', ['lux.services'])
        //
        .constant('luxCodemirrorDefaults', {
            lineWrapping : true,
            lineNumbers: true,
            mode: lux.context.CODEMIRROR_MODE || "markdown",
            theme: lux.context.CODEMIRROR_THEME || "monokai",
            reindentOnLoad: true,
        })
        //
        .directive('luxCodemirror', ['$lux', 'luxCodemirrorDefaults', function ($lux, luxCodemirrorDefaults) {
            //
            // Initialize codemirror, load css.
            function initCodemirror() {
                loadCss('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.3.0/codemirror.css');
                loadCss('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.3.0/theme/' + luxCodemirrorDefaults.theme + '.css');
            }
            //
            // Creates a new instance of the editor
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
            // Allows play with ng-model
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
            // Set specified mode
            function setMode(options) {
                switch (options.mode) {
                    case 'json':
                        options.mode = 'javascript';
                        break;
                    case 'html':
                        options.mode = 'htmlmixed';
                        break;
                    default:
                        options.mode = luxCodemirrorDefaults.mode;
                        break;
                }
                return options;
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

                    // Initialize codemirror
                    initCodemirror();

                    return {
                        post: function(scope, element, attrs, ngModel) {

                            var options = angular.extend(
                                { value: element.text() },
                                luxCodemirrorDefaults || {}
                            );

                            if (attrs.luxCodemirror) {
                                var luxCodemirrorOpts = JSON.parse(attrs.luxCodemirror);

                                if (options.hasOwnProperty('mode'))
                                    luxCodemirrorOpts = setMode(luxCodemirrorOpts);

                                angular.extend(
                                    options,
                                    luxCodemirrorOpts || {}
                                );
                            }

                            var codemirror = newEditor(element, options);

                            ngModelLink(codemirror, ngModel, scope);

                            // Allow access to the CodeMirror instance through a broadcasted event
                            // eg: $broadcast('CodeMirror', function(cm){...});
                            scope.$on('CodeMirror', function(event, callback) {
                                if (angular.isFunction(callback))
                                    callback(codemirror);
                                else
                                    throw new Error('the CodeMirror event requires a callback function');
                            });

                            scope.$on('$viewContentLoaded', function () {
                                codemirror.refresh();
                            });
                        }
                    };
                }
            };
        }]);
