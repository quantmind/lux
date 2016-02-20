define(['angular',
        'lux/forms/main'], function (angular, lux) {
    'use strict';
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
            lineWrapping: true,
            lineNumbers: true,
            mode: 'markdown',
            theme: lux.context.CODEMIRROR_THEME || 'monokai',
            reindentOnLoad: true,
            indentUnit: 4,
            indentWithTabs: true,
            htmlModes: ['javascript', 'xml', 'css', 'htmlmixed'],
            url: 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.3.0'
        })
        //
        .run([function () {
            lux.forms.directives.push(function(scope, element) {
                // lux-codemirror directive
                if (scope.field.hasOwnProperty('text_edit'))
                    element.attr('lux-codemirror', scope.field.text_edit);
            });
        }])
        //
        .directive('luxCodemirror', ['$window', '$lux', 'luxCodemirrorDefaults',
            function ($window, $lux, luxCodemirrorDefaults) {
                //
                return {
                    restrict: 'EA',
                    require: '?ngModel',
                    //
                    compile: function () {
                        loadCSS();
                        return {
                            post: codemirror
                        };
                    }
                };

                function codemirror(scope, element, attrs, ngModel) {
                    var options = setMode(angular.extend(
                            {value: element.text()},
                            luxCodemirrorDefaults,
                            scope.$eval(attrs.luxCodemirror)
                        )),
                        jsModuleSuffix = getJSModuleSuffix(options.mode);

                    require(['codemirror-' + jsModuleSuffix], function () {
                        // Require CodeMirror
                        if (angular.isUndefined($window.CodeMirror)) {
                            throw new Error('lux-codemirror needs CodeMirror to work!');
                        }

                        scope.cm = newEditor(element, options);
                        ngModelLink(ngModel, scope);

                        scope.$on('$viewContentLoaded', function () {
                            scope.cm.refresh();
                        });
                        scope.$emit('CodeMirror', scope.cm);
                    });
                }

                //
                // Initialize codemirror, load css.
                function loadCSS() {
                    lux.loadCss(luxCodemirrorDefaults.url + '/codemirror.css');
                    lux.loadCss(luxCodemirrorDefaults.url + '/theme/' + luxCodemirrorDefaults.theme + '.css');
                }

                //
                // Creates a new instance of the editor
                function newEditor(element, options) {
                    if (element[0].tagName === 'TEXTAREA') {
                        return $window.CodeMirror.fromTextArea(element[0], options);
                    } else {
                        element.html('');
                        return new $window.CodeMirror(function (cm_el) {
                            element.append(cm_el);
                        }, options);
                    }
                }

                //
                // Allows play with ng-model
                function ngModelLink(ngModel, scope) {
                    if (!ngModel) return;

                    // CodeMirror expects a string, so make sure it gets one.
                    // This does not change the model.
                    ngModel.$formatters.push(function (value) {
                        if (angular.isUndefined(value) || value === null)
                            return '';
                        else if (angular.isObject(value) || angular.isArray(value))
                            throw new Error('codemirror cannot use an object or an array as a model');
                        return value;
                    });

                    // Override the ngModelController $render method, which is what gets called when the model is updated.
                    // This takes care of the synchronizing the codeMirror element with the underlying model, in the case that it is changed by something else.
                    ngModel.$render = function () {
                        var safeViewValue = ngModel.$viewValue || '';
                        scope.cm.setValue(safeViewValue);
                    };

                    // Keep the ngModel in sync with changes from CodeMirror
                    scope.cm.on('change', function (instance) {
                        var newValue = instance.getValue();
                        if (newValue !== ngModel.$viewValue) {
                            scope.$evalAsync(function () {
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
                        case 'python':
                            options.mode = 'python';
                            break;
                        default:
                            options.mode = luxCodemirrorDefaults.mode;
                            break;
                    }
                    return options;
                }

                //
                // Returns suffix of the js module name to load depending on the editor mode
                function getJSModuleSuffix(modeName) {
                    if (luxCodemirrorDefaults.htmlModes.indexOf(modeName) >= 0) {
                        return 'htmlmixed';
                    } else if (modeName === 'python') {
                        return 'python';
                    } else {
                        return 'markdown';
                    }
                }
            }
        ]);

});
