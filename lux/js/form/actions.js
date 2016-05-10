
export default function (ngModule) {

    // @ngInject
    ngModule.config(addActions);


    function addActions(luxFormConfigProvider) {
        var cfg = luxFormConfigProvider;

        cfg.setAction('submit', submitForm);

        cfg.onSuccess('default', defaultOnSuccess);
    }

}


function submitForm (e) {

    var form = this.$form,
        $lux = this.$lux,
        $cfg = this.$cfg,
        info = this.info,
        action = info.action;

    if (!action) return;

    e.preventDefault();
    e.stopPropagation();

    var api = $lux.api(action);

    // Flag the form as submitted
    form.$setSubmitted();
    //
    // Invalid?
    if (form.$invalid)
        form.$setDirty();
        // return this.$lux.messages.info('Invalid form - not submitting');

    form.$pending = true;
    $lux.messages.clear(info.id);

    var ct = (info.enctype || '').split(';')[0],
        method = info.method || 'post',
        options = {data: info.model};

    if (ct === 'application/x-www-form-urlencoded' || ct === 'multipart/form-data')
        options.headers = {
            'content-type': undefined
        };

    api.request(method, options).then(success, failure);


    function success (response) {
        form.$pending = false;
        var hook = $cfg.onSuccess(info.resultHandler);
        hook(response, info);
    }

    function failure (response) {
        form.$pending = false;
        var data = response.data || {},
            errors = data.errors;

        if (!errors) {
            errors = data.message;
            if (!errors) {
                var status = response.status || data.status || 501;
                errors = 'Response error (' + status + ')';
            }
        }
        info.addMessages(errors, 'error');
    }
}


function defaultOnSuccess (response, form) {
    var data = response.data,
        messages = data.messages;

    if (!messages) {
        messages = data.message;
        if (!messages) {
            if (response.status === 201)
                messages = 'Successfully created';
            else
                messages = 'Successfully updated';
        }
    }

    form.addMessages(messages);
}
