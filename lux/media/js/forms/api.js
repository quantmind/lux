define(['angular',
        'lux/main'], function (angular, lux) {
    'use strict';

    angular.module('lux.form.api', ['lux.services'])

        .factory('formApi', ['$lux', function ($lux) {

            return {
                ready: formReady
            };

            function formReady (scope) {
                var model = scope[scope.formModelName];

                var attrs = scope.formAttrs,
                    action = attrs ? attrs.action : null,
                    promise;

                if (lux.isObject(action)) {
                    var api = $lux.api(action);
                    if (api) {
                        $lux.log.info('Form ' + scope.formModelName + ' registered with "' +
                            api.toString() + '" api');
                        promise = api.formReady();
                    }
                }

                if (promise) promise.success(formData).error(emit);
                else emit();

                function emit() {
                    scope.$emit('formReady', model, scope);
                }

                function formData (data) {
                    lux.forEach(data, function (value, key) {
                        // TODO: do we need a callback for JSON fields?
                        // or shall we leave it here?

                        var modelType = scope[scope.formModelName + 'Type'];
                        var jsonArrayKey = key.split('[]')[0];

                        // Stringify json only if has json mode enabled
                        if (modelType[jsonArrayKey] === 'json' && lux.isJsonStringify(value)) {

                            // Get rid of the brackets from the json array field
                            if (angular.isArray(value)) {
                                key = jsonArrayKey;
                            }

                            value = angular.toJson(value, null, 4);
                        }

                        if (angular.isArray(value)) {
                            model[key] = [];
                            angular.forEach(value, function (item) {
                                model[key].push(item.id || item);
                            });
                        } else {
                            model[key] = value.id || value;
                        }
                    });
                    emit();
                }
            }
        }]);

});
