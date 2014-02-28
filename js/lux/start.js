define(['lodash', 'jquery'], function (_, $) {
    "use strict";

    var

    root = window,
    //
    prev_lux = root.lux,
    //
    slice = Array.prototype.slice;
    //
    lux = root.lux = {
        //
        debug: false,
        //
        skins: [],
        //
        // Container of libraries used by lux
        libraries: [],
        //
        media_url: '/media/',
        //
        icon: 'fontawesome',
        //
        data_api: true,
        //
        set_value_hooks: [],
        //
        // Set the ``value`` for ``elem``
        //
        //  This is generalised value setting method which tries
        //  the ``set_value_hooks`` functions first, and if none of them
        //  return ``true`` it reverts to the standard ``elem.val`` method.
        setValue: function (elem, value) {
            var hook;
            for (var i=0; i<lux.set_value_hooks.length; i++) {
                if (lux.set_value_hooks[i](elem, value)) {
                    return;
                }
            }
            elem.val(value);
        },
        //
        addLib: function (info) {
            if (!_.contains(lux.libraries, info.name)) {
                lux.libraries.push(info);
            }
        },
        //
        // Create a random s4 string
        s4: function () {
            return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
        },
        //
        // Create a UUID4 string
        guid: function () {
            var S4 = lux.s4;
            return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
        },
        //
        isnothing: function (el) {
            return el === undefined || el === null;
        },
        //
        sorted: function (obj, callback) {
            var sortable = [];
            _(obj).forEch(function (elem, name) {
                sortable.push(name);
            });
            sortable.sort();
            _(sortable).forEach(function (name) {
                callback(obj[name], name);
            });
        },
        //
        niceStr: function (s) {
            return s.capitalize().replace('_', ' ');
        }
    };

    String.prototype.capitalize = function() {
        return this.charAt(0).toUpperCase() + this.slice(1);
    };

    lux.addLib({name: 'RequireJs', web: 'http://requirejs.org/', version: require.version});
    lux.addLib({name: 'Lo-Dash', web: 'http://lodash.com/', version: _.VERSION});
    lux.addLib({name: 'jQuery', web: 'http://jquery.com/', version: $.fn.jquery});

