/**
 * Created by Reupen on 02/06/2015.
 */

angular.module('lux.form.utils', ['lux.services'])

    .directive('remoteOptions', ['$lux', function ($lux) {

        function link(scope, element, attrs, ctrl) {
            var id = attrs.bmllRemoteoptionsId || 'id',
                name = attrs.bmllRemoteoptionsValue || 'name';

            var options = scope[attrs.bmllRemoteoptionsName] = [];

            var initialValue = {};
            initialValue[id] = '';
            initialValue[name] = 'Loading...';

            options.push(initialValue);
            ctrl.$setViewValue('');
            ctrl.$render();

            var promise = api.get({name: attrs.bmllRemoteoptionsName});
            promise.then(function (data) {
                options[0][name] = 'Please select...';
                options.push.apply(options, data.data.result);
            }, function (data) {
                /** TODO: add error alert */
                options[0][name] = '(error loading options)';
            });
        }

        return {
            require: 'ngModel',
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
