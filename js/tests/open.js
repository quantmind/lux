require(['../../lux/media/lux/lux.js', 'angular-mocks'], function (lux) {
    "use strict";
    lux.add_ready_callback(function () {
    //
    //
    function luxInjector () {
        return angular.injector(['ng', 'ngMock', 'lux']);
    }
