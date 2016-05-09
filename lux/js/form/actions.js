
export default function (ngModule) {

    // @ngInject
    ngModule.config(addActions);


    function addActions(luxFormConfigProvider) {
        luxFormConfigProvider.setAction('submit', submitForm);
    }

}

function submitForm (e) {

    var form = this.$form,
        action = form.$action;

    if (!action) return;

    e.preventDefault();
    e.stopPropagation();

    var api = this.$lux.api(action);

    // Flag the form as submitted
    form.$setSubmitted();
    //
    // Invalid?
    if (form.$invalid) {
        form.$setDirty();
        this.$log.info('Invalid form - not submitting');
        return;
    }
}
