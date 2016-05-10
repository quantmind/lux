
// @ngInject
export default function ($window, luxFormConfig) {

    luxFormConfig.onSuccess('redirect', function (response, form) {
        $window.location.href = form.redirectTo || '/';
    }).onSuccess('reload', function () {
        $window.location.reload();
    });

}
