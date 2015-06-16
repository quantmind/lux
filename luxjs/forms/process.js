//
//	Form processor
//	=========================
//
//	Default Form processing function
// 	If a submit element (input.submit or button) does not specify
// 	a ``click`` entry, this function is used
lux.processForm = function (e) {

    e.preventDefault();
    e.stopPropagation();

    var form = this[this.formName],
        model = this[this.formModelName],
        attrs = this.formAttrs,
        target = attrs.action,
        scope = this,
        FORMKEY = scope.formAttrs.FORMKEY,
        $lux = this.$lux,
        method = attrs.method || 'post',
        promise,
        api;
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
    if (api) {
        promise = api.request(method, target, model);
    } else if (target) {
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
    } else {
        $lux.log.error('Could not process form. No target or api');
        return;
    }
    //
    promise.then(function (response) {
            var data = response.data;
            var hookName = scope.formAttrs.resultHandler;
            var processedByHook = hookName && scope.$parent[hookName](response);
            if (!processedByHook) {
                if (data.messages) {
                    scope.addMessages(data.messages);
                } else if (api) {
                    // Created
                    if (response.status === 201) {
                        scope.formMessages[FORMKEY] = [{message: 'Successfully created'}];
                    } else {
                        scope.formMessages[FORMKEY] = [{message: 'Successfully updated'}];
                    }
                } else {
                    window.location.href = data.redirect || '/';
                }
            }
        },
        function (response) {
            var data = response.data,
                status = response.status,
                messages, msg;
            if (data) {
                messages = data.messages;
                if (!messages) {
                    msg = data.message;
                    if (!msg) {
                        status = status || data.status || 501;
                        msg = 'Server error (' + data.status + ')';
                    }
                    messages = {};
                    scope.formMessages[FORMKEY] = [{
                        message: msg,
                        error: true
                    }];
                } else
                    scope.addMessages(messages);
            } else {
                status = status || 501;
                msg = 'Server error (' + status + ')';
                messages = {};
                scope.formMessages[FORMKEY] = [{message: msg, error: true}];
            }
        });
};
