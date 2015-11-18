//
function joinField(model, name, extra) {
    return model + '["' + name + '"].' + extra;
}

angular.module('lux.form.process', ['ngFileUpload'])
    .run(['$lux', 'Upload', function ($lux, Upload) {

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
                $lux = scope.$lux,
                form = this[this.formName],
                model = this[this.formModelName],
                attrs = this.formAttrs,
                target = attrs.action,
                FORMKEY = scope.formAttrs.FORMKEY,
                method = attrs.method || 'post',
                uploadHeaders = {},
                promise,
                api,
                uploadUrl;
            //
            // Flag the form as submitted
            form.submitted = true;
            if (form.$invalid) return;

            // Get the api information if target is an object
            //	target
            //		- name:	api name
            //		- target: api target
            if (isObject(target)) api = $lux.api(target);

            this.formMessages = {};
            //
            if (scope.formProcessor === 'ngf') {
                if (api) {
                    promise = api.getApiUrls().then(function(apiUrls) {
                        uploadUrl = apiUrls[target.name];
                        if (target.path) {
                            uploadUrl = joinUrl(uploadUrl, target.path);
                        }
                        uploadHeaders.Authorization = 'bearer ' + api.token();
                    });
                } else {
                    promise = $lux.q.defer();
                    uploadUrl = target;
                    promise.resolve();
                }
                promise = promise.then(function() {
                    return Upload.upload({
                        url: uploadUrl,
                        headers: uploadHeaders,
                        data: model
                    });
                });
            } else if (api) {
                promise = api.request(method, target, model);
            } else if (target) {
                var enctype = attrs.enctype || 'application/json',
                    ct = enctype.split(';')[0],
                    options = {
                        url: target,
                        method: attrs.method || 'POST',
                        data: model,
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
                promise = $lux.http(options);
            } else {
                $lux.log.error('Could not process form. No target or api');
                return;
            }
            //
            promise.then(function (response) {
                    var data = response.data;
                    var hookName = scope.formAttrs.resultHandler;
                    var hook = hookName && $lux.formHandlers[hookName];
                    if (hook) {
                        hook(response, scope);
                    } else if (data.messages) {
                        scope.addMessages(data.messages);
                    } else if (api) {
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
                    var data = response.data || {},
                        status = response.status,
                        messages = data.errors,
                        msg;
                    if (!messages) {
                        msg = data.message;
                        if (!msg) {
                            status = status || data.status || 501;
                            msg = 'Response error (' + data.status + ')';
                        }
                        messages = [{message: msg}];
                    }
                    scope.addMessages(messages, 'error');
                });
        };
    }]);