import _ from '../ng';
import querySelector from '../core/querySelector';

const aceTemplate = `<div class="ace-lux">
<div ng-if="aceHeader" class="ace-lux-header" lux-navbar="aceHeader"></div>
<div class="ace-lux-editor"></div>
</div>`;


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
            element,
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
            element = _.element(aceTemplate);
            el.after(element).css('display', 'none');
            element = querySelector(element, '.ace-lux-editor');
            editor = ace.edit(element[0]);
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
            var options = _.extend({}, opts);
            delete options.theme;
            delete options.mode;
            editor.setOptions(options);

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
        }
    }
}
