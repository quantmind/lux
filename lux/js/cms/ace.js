import _ from '../ng';

// load ace with require
// https://github.com/ajaxorg/ace-builds/issues/35

// @ngInject
export default function ($lux) {

    return {
        restrict: 'EA',
        require: '?ngModel',
        link: linkAce
    };

    function linkAce(scope, el, attrs, ngModel) {

        var ace,
            editor,
            session,
            text = '',
            onChangeListener,
            onBlurListener,
            opts = _.extend({
                showGutter: true,
                theme: 'twilight',
                mode: 'markdown',
                tabSize: 4
            }, $lux.context.ace, scope.$eval(attrs.luxAce));

        $lux.lazy.require(['ace/ace'], startAce);

        // Bind to the Model
        if (ngModel) {
            ngModel.$formatters.push(function (value) {
                if (_.isUndefined(value) || value === null) {
                    return '';
                }
                else if (_.isObject(value) || _.isArray(value)) {
                    throw new Error('ui-ace cannot use an object or an array as a model');
                }
                return value;
            });

            ngModel.$render = function () {
                if (session) session.setValue(ngModel.$viewValue);
                else text = ngModel.$viewValue;
            };
        }

        // Start Ace editor
        function startAce(_ace) {
            ace = _ace;
            ace.config.set("packaged", true);
            ace.config.set("basePath", require.toUrl("ace"));
            //
            editor = ace.edit(el[0]);
            session = editor.getSession();
            session.setValue(text);
            updateOptions();

            el.on('$destroy', function () {
                editor.session.$stopWorker();
                editor.destroy();
            });

            scope.$watch(function() {
                return [el[0].offsetWidth, el[0].offsetHeight];
            }, function() {
                editor.resize();
                editor.renderer.updateFull();
            }, true);
        }

        function updateOptions () {

            // unbind old change listener
            session.removeListener('change', onChangeListener);
            onChangeListener = onChange(opts.onChange);
            session.on('change', onChangeListener);

            // unbind old blur listener
            editor.removeListener('blur', onBlurListener);
            onBlurListener = onChange(opts.onBlur);
            session.on('blur', onBlurListener);

            setOptions();
        }

        function onChange (callback) {

            return function (e) {
                var newValue = session.getValue();

                if (ngModel && newValue !== ngModel.$viewValue &&
                    // HACK make sure to only trigger the apply outside of the
                    // digest loop 'cause ACE is actually using this callback
                    // for any text transformation !
                    !scope.$$phase && !scope.$root.$$phase) {
                    scope.$evalAsync(function () {
                        ngModel.$setViewValue(newValue);
                    });
                }

                executeUserCallback(callback, e);
            };
        }

        function onBlur (callback) {
            return function () {
                executeUserCallback(callback);
            };
        }

        function executeUserCallback (callback) {
            if (_.isDefined(callback)) {
                var args = Array.prototype.slice.call(arguments, 1);

                scope.$evalAsync(() => {
                    callback.apply(editor, args);
                });
            }
        }

        function setOptions() {

            editor.setTheme(`ace/theme/${opts.theme}`);
            session.setMode(`ace/mode/${opts.mode}`);
            session.setTabSize(opts.tabSize);

            // sets the ace worker path, if running from concatenated
            // or minified source
            if (_.isDefined(opts.workerPath)) {
                var config = window.ace.require('ace/config');
                config.set('workerPath', opts.workerPath);
            }
            // ace requires loading
            if (_.isDefined(opts.require)) {
                opts.require.forEach(function (n) {
                    window.ace.require(n);
                });
            }
            // Boolean options
            if (_.isDefined(opts.showGutter)) {
                editor.renderer.setShowGutter(opts.showGutter);
            }
            if (_.isDefined(opts.useWrapMode)) {
                session.setUseWrapMode(opts.useWrapMode);
            }
            if (_.isDefined(opts.showInvisibles)) {
                editor.renderer.setShowInvisibles(opts.showInvisibles);
            }
            if (_.isDefined(opts.showIndentGuides)) {
                editor.renderer.setDisplayIndentGuides(opts.showIndentGuides);
            }
            if (_.isDefined(opts.useSoftTabs)) {
                session.setUseSoftTabs(opts.useSoftTabs);
            }
            if (_.isDefined(opts.showPrintMargin)) {
                editor.setShowPrintMargin(opts.showPrintMargin);
            }

            // commands
            if (_.isDefined(opts.disableSearch) && opts.disableSearch) {
                editor.commands.addCommands([
                    {
                        name: 'unfind',
                        bindKey: {
                            win: 'Ctrl-F',
                            mac: 'Command-F'
                        },
                        exec: function () {
                            return false;
                        },
                        readOnly: true
                    }
                ]);
            }

            // Basic options
            if (_.isString(opts.theme)) {
                editor.setTheme('ace/theme/' + opts.theme);
            }
            if (_.isString(opts.mode)) {
                session.setMode('ace/mode/' + opts.mode);
            }
            // Advanced options
            if (_.isDefined(opts.firstLineNumber)) {
                if (_.isNumber(opts.firstLineNumber)) {
                    session.setOption('firstLineNumber', opts.firstLineNumber);
                } else if (_.isFunction(opts.firstLineNumber)) {
                    session.setOption('firstLineNumber', opts.firstLineNumber());
                }
            }

            // advanced options
            var key, obj;
            if (_.isDefined(opts.advanced)) {
                for (key in opts.advanced) {
                    // create a javascript object with the key and value
                    obj = {name: key, value: opts.advanced[key]};
                    // try to assign the option to the ace editor
                    editor.setOption(obj.name, obj.value);
                }
            }

            // advanced options for the renderer
            if (_.isDefined(opts.rendererOptions)) {
                for (key in opts.rendererOptions) {
                    // create a javascript object with the key and value
                    obj = {name: key, value: opts.rendererOptions[key]};
                    // try to assign the option to the ace editor
                    editor.renderer.setOption(obj.name, obj.value);
                }
            }

            // onLoad callbacks
            _.forEach(opts.callbacks, function (cb) {
                if (_.isFunction(cb)) {
                    cb(editor);
                }
            });
        }
    }
}
