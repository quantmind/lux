define(['jquery', 'lux-web'], function ($, web) {
    //
    web.visual_tests = {};
    web.visual_test = function (test, callable) {
        web.visual_tests[test] = callable;
    };
