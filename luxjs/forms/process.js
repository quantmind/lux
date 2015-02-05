    // Default Form processing function
    // If a submit element (input.submit or button) does not specify
    // a ``click`` entry, this function is used
    lux.processForm = function (e) {
        e.preventDefault();
        e.stopPropagation();
        var form = this[this.formName],
            model = this[this.formModelName],
            attrs = this.formAttrs,
            target = attrs.action,
            apiname = attrs.apiname,
            scope = this,
            FORMKEY = scope.formAttrs.FORMKEY,
            $lux = this.$lux,
            promise,
            api;
        //
        // Flag the form as submitted
        form.submitted = true;
        if (form.$invalid) {
            return;
        }

        // Get the api information
        if (!target && apiname) {
            api = $lux.api(apiname);
            if (!api)
                $lux.log.error('Could not find api url for ' + apiname);
        }

        this.formMessages = {};
        //
        if (target) {
            var enctype = attrs.enctype || '',
                ct = enctype.split(';')[0],
                options = {
                    url: target,
                    method: attrs.method || 'POST',
                    data: model,
                    transformRequest: $lux.formData(ct),
                };
            // Let the browser choose the content type
            if (ct === 'application/x-www-form-urlencoded' || ct === 'multipart/form-data') {
                options.headers = {
                    'content-type': undefined
                };
            }
            promise = $lux.http(options);
        } else if (api) {
            promise = api.put($scope.formModel);
        } else {
            $lux.log.error('Could not process form. No target or api');
            return;
        }
        //
        promise.success(function(data, status) {
            if (data.messages) {
                scope.addMessages(data.messages);
            } else if (api) {
                // Created
                if (status === 201) {
                    scope.formMessages[FORMKEY] = [{message: 'Succesfully created'}];
                } else {
                    scope.formMessages[FORMKEY] = [{message: 'Succesfully updated'}];
                }
            } else {
                window.location.href = data.redirect || '/';
            }
        }).error(function(data, status, headers) {
            var messages, msg;
            if (data) {
                messages = data.messages;
                if (!messages) {
                    msg = data.message;
                    if (!msg) {
                        status = status || data.status || 501;
                        msg = 'Server error (' + data.status + ')';
                    }
                    messages = {};
                    scope.formMessages[FORMKEY] = [{message: msg, error: true}];
                }
            } else {
                status = status || 501;
                msg = 'Server error (' + data.status + ')';
                messages = {};
                scope.formMessages[FORMKEY] = [{message: msg, error: true}];
            }
        });
    };