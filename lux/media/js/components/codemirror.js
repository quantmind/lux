define(['angular', 'lux'], function (angular, lux) {
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
        .directive('luxCodemirror', ['$lux', 'luxCodemirrorDefaults',
            function ($lux, luxCodemirrorDefaults) {
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
                    var jsModuleSuffix,
                        options = angular.extend(
                            {value: element.text()},
                            luxCodemirrorDefaults || {},
                            scope.$eval(attrs.luxCodemirror) || {}
                        );

                    options = setMode(options);
                    jsModuleSuffix = getJSModuleSuffix(options.mode);

                    require(['codemirror-' + jsModuleSuffix], function () {
                        // Require CodeMirror
                        if (angular.isUndefined($lux.window.CodeMirror)) {
                            throw new Error('lux-codemirror needs CodeMirror to work!');
                        }

                        var cm = newEditor(element, options);

                        ngModelLink(cm, ngModel, scope);

                        // Allow access to the CodeMirror instance through a broadcasted event
                        // eg: $broadcast('CodeMirror', function(cm){...});
                        scope.$on('CodeMirror', function (event, callback) {
                            if (angular.isFunction(callback))
                                callback(cm);
                            else
                                throw new Error('the CodeMirror event requires a callback function');
                        });

                        scope.$on('$viewContentLoaded', function () {
                            cm.refresh();
                        });
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
                    var cm;

                    if (element[0].tagName === 'TEXTAREA') {
                        cm = $lux.window.CodeMirror.fromTextArea(element[0], options);
                    } else {
                        element.html('');
                        cm = new $lux.window.CodeMirror(function (cm_el) {
                            element.append(cm_el);
                        }, options);
                    }

                    return cm;
                }

                //
                // Allows play with ng-model
                function ngModelLink(cm, ngModel, scope) {
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
                        cm.setValue(safeViewValue);
                    };

                    // Keep the ngModel in sync with changes from CodeMirror
                    cm.on('change', function (instance) {
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
