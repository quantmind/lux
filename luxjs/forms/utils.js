/**
 * Created by Reupen on 02/06/2015.
 */

angular.module('lux.form.utils', ['lux.services'])

    .directive('remoteOptions', ['$lux', function ($lux) {

        function fill(api, target, scope, attrs) {

            var id = attrs.remoteOptionsId || 'id',
                name = attrs.remoteOptionsValue || 'id',
                initialValue = {},
                options = [];

            scope[target.name] = options;
            initialValue.id = '';
            initialValue.name = 'Loading...';

            options.push(initialValue);

            api.get().then(function (data) {
                options[0].name = 'Please select...';
                scope[scope.formModelName][attrs.name] = '';
                angular.forEach(data.data.result, function (val) {
                    options.push({
                        id: val[id],
                        name: val[name]
                    });
                });
            }, function (data) {
                /** TODO: add error alert */
                options[0] = '(error loading options)';
            });
            scope[scope.formModelName][attrs.name] = '';
        }

        function link(scope, element, attrs) {

            if (attrs.remoteOptions) {
                var target = JSON.parse(attrs.remoteOptions),
                    api = $lux.api(target);

                if (api && target.name)
                    return fill(api, target, scope, attrs);
            }
            // TODO: message
        }

        return {
            link: link
        };
    }])

    .directive('selectOnClick', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                element.on('click', function () {
                    if (!window.getSelection().toString()) {
                        // Required for mobile Safari
                        this.setSelectionRange(0, this.value.length);
                    }
                });
            }
        };
    });
