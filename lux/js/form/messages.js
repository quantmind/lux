export default function (ngModule) {
    ngModule.config(errorMessages);

    // @ngInject
    function errorMessages(luxFormConfigProvider) {
        var p = luxFormConfigProvider;

        p.error('minlength', function (field) {
            return `${field.label} length should be more than ${field.ngField.$viewValue.length}`;
        });

        p.error('maxlength', function (field) {
            return `${field.label} length should be less than ${field.ngField.$viewValue.length}`;
        });

        p.error('required', function (field) {
            return `${field.label} is required`;
        });

    }
}
