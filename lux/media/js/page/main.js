define(['angular',
        'lux/main',
        'lux/page/page'], function (angular, lux) {
    'use strict';
    //
    //	Lux.router
    //	===================
    //
    //	Drop in replacement for lux.ui.router when HTML5_NAVIGATION is off.
    //
    angular.module('lux.router', ['lux.page'])
        //
        .config(['$locationProvider', function ($locationProvider) {
            //
            // Enable html5mode but set the hash prefix to something different from #
            $locationProvider.html5Mode({
                enabled: true,
                requireBase: false,
                rewriteLinks: false
            }).hashPrefix("#");
        }]);

    return lux;
});
