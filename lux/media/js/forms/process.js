define(['angular',
        'lux/main',
        'lux/forms/handlers'], function (angular, lux) {
    'use strict';

    var formProcessors = {};

    angular.module('lux.form.process', [])

        .run(['$lux', function ($lux) {

            //
            //	Form processor
            //	=========================
            //
            //	Default Form processing function
            // 	If a submit element (input.submit or button) does not specify
            // 	a ``click`` entry, this function is used
            //
            //  Post Result
            //  -------------------
            //
            //  When a form is processed succesfully, this method will check if the
            //  ``formAttrs`` object contains a ``resultHandler`` parameter which should be
            //  a string.
            //
            //  In the event the ``resultHandler`` exists,
            //  the ``$lux.formHandlers`` object is checked if it contains a function
            //  at the ``resultHandler`` value. If it does, the function is called.
            lux.processForm = function (e) {

                e.preventDefault();
                e.stopPropagation();

                var scope = this,
                    process = formProcessor($lux, scope);

                // Flag the form as submitted
                process.form.$setSubmitted();
                //
                // Invalid?
                if (process.form.$invalid) {
                    process.form.$setDirty();
                    return;
                }
                //
                var promise = process();

                if (!promise) {
                    $lux.log.error('Could not process form. No target or api');
                    return;
                }
                //
                promise.then(
                    function (response) {
                        var data = getData(response);
                        var hookName = process.attrs.resultHandler;
                        var hook = hookName && $lux.formHandlers[hookName];
                        if (hook) {
                            hook(response, scope);
                        } else if (data.messages) {
                            scope.addMessages(data.messages);
                        } else if (process.api) {
                            // Created
                            var message = data.message;
                            if (!message) {
                                if (response.status === 201)
                                    message = 'Successfully created';
                                else
                                    message = 'Successfully updated';
                            }
                            $lux.messages.info(message);
                        }
                    },
                    function (response) {
                        var data = getData(response);

                        if (data.errors) {
                            scope.addMessages(data.errors, 'error');
                        } else {
                            var message = data.message;
                            if (!message) {
                                var status = status || data.status || 501;
                                message = 'Response error (' + status + ')';
                            }
                            $lux.messages.error(message);
                        }
                    });

                function getData (response) {
                    process.form.$pending = false;
                    return response.data || {};
                }
            };
        }]);

    formProcessors.default = function ($lux, p) {

        if (p.api) {
            return p.api.request(p.method, p.target, p.model);
        } else if (p.target) {
            var enctype = p.attrs.enctype || 'application/json',
                ct = enctype.split(';')[0],
                options = {
                    url: p.target,
                    method: p.method,
                    data: p.model,
                    transformRequest: $lux.formData(ct)
                };
            // Let the browser choose the content type
            if (ct === 'application/x-www-form-urlencoded' || ct === 'multipart/form-data') {
                options.headers = {
                    'content-type': undefined
                };
            } else {
                options.headers = {
                    'content-type': ct
                };
            }
            return $lux.http(options);
        }
    };

    return formProcessors;

    //
    //  Create a form processor with all the form information as atributes
    function formProcessor ($lux, scope) {

        var form = scope[scope.formName];

        function process () {
            var _process = formProcessors[scope.formProcessor || 'default'];
            // set as pending
            form.$pending = true;
            // clear form messages
            scope.formMessages = {};
            return _process($lux, process);
        }

        process.form = form;
        process.model = scope[scope.formModelName];
        process.attrs = scope.formAttrs;
        process.target = scope.formAttrs.action;
        process.method = scope.formAttrs.method || 'post';
        process.api = angular.isObject(process.target) ? $lux.api(process.target) : null;

        return process;
    }
});
