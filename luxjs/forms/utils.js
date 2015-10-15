/**
 * Created by Reupen on 02/06/2015.
 */

angular.module('lux.form.utils', ['lux.services'])

    .directive('remoteOptions', ['$lux', function ($lux) {

        function fill(api, target, scope, attrs) {

            var id = attrs.remoteOptionsId || 'id',
                nameOpts = attrs.remoteOptionsValue ? JSON.parse(attrs.remoteOptionsValue) : {
                    type: 'field',
                    source: 'id'
                },
                nameFromFormat = nameOpts.type === 'formatString',
                initialValue = {},
                params = JSON.parse(attrs.remoteOptionsParams || '{}'),
                options = [];

            scope[target.name] = options;

            initialValue.id = '';
            initialValue.name = 'Loading...';

            options.push(initialValue);

            api.get(null, params).then(function (data) {
                if (attrs.multiple) {
                    options.splice(0, 1);
                } else {
                    options[0].name = 'Please select...';
                }
                angular.forEach(data.data.result, function (val) {
                    var name;
                    if (nameFromFormat) {
                        name = formatString(nameOpts.source, val);
                    } else {
                        name = val[nameOpts.source];
                    }
                    options.push({
                        id: val[id],
                        name: name
                    });
                });
            }, function (data) {
                /** TODO: add error alert */
                options[0] = '(error loading options)';
            });
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
