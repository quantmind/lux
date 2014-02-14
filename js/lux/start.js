define(['lodash', 'jquery'], function () {
    "use strict";

    var root = window,
        lux = {
            //version: "<%= pkg.version %>"
        },
        slice = Array.prototype.slice;
    //
    root.lux = lux;
    //
    // Showdown extensions
    lux.showdown = {};
    //
    // Create a random s4 string
    lux.s4 = function () {
        return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    };
    //
    // Create a UUID4 string
    lux.guid = function () {
        var S4 = lux.s4;
        return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
    };
    //
    lux.isnothing = function (el) {
        return el === undefined || el === null;
    };
    //
    lux.sorted = function (obj, callback) {
        var sortable = [];
        _(obj).forEch(function (elem, name) {
            sortable.push(name);
        });
        sortable.sort();
        _(sortable).forEach(function (name) {
            callback(obj[name], name);
        });
    };
    //
    // Create a lux event handler (proxy for a jQuery event)
    lux.event = function () {
        return $.Event();
    };