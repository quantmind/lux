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
    angular.module('lux.router', ['lux.page']);

    return lux;
});
