define(['lux/forms',
        'angular',
        'angular-file-upload'], function (lux) {
    "use strict";

    angular.module('lux.form.fileupload', ['lux.form', 'ngFileUpload'])

        .run(['$q', 'Upload', function ($q, Upload) {
            lux.forms.directives.file = function (scope, element) {
                if (scope.formAttrs.useNgFileUpload && scope.field.type === 'file') {
                    element.attr('ngf-select', '');
                    scope.formProcessor = 'ngFileUpload';
                }
            };

            lux.forms.processors.ngFileUpload = function ($lux, process) {
                var uploadUrl = process.target,
                    api = process.api,
                    uploadHeaders = {},
                    promise;

                if (api) {
                    promise = api.getUrlForTarget(target).then(function (url) {
                        uploadUrl = url;
                        uploadHeaders.Authorization = 'bearer ' + api.token();
                    });
                } else {
                    var deferred = $q.defer();
                    deferred.resolve();
                    promise = deferred.promise;
                }

                return promise.then(function () {
                    return Upload.upload({
                        url: uploadUrl,
                        headers: uploadHeaders,
                        data: process.model
                    });
                });
            };

        }]);
});
