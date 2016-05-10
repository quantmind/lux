
// @ngInject
export default function ($window, luxFormConfig) {

    var cfg = luxFormConfig;

    cfg.setOnSuccess('redirect', function (response, form) {
        $window.location.href = form.redirectTo || '/';
    });

    cfg.setOnSuccess('reload', function () {
        $window.location.reload();
    });

}
