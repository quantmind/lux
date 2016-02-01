define([], function () {
    'use strict';

    return events;

    function events () {

        var events = {};

        return {
            bind: bind,
            unbind: unbind,
            fire: fire
        };

        function bind (event, callback) {
            var callbacks = events[event];
            if (!callbacks) {
                callbacks = [];
                events[event] = callbacks;
            }
            callbacks.push(callback);
            return self;
        }

        function unbind (event, callback) {
            var callbacks = events[event];
            if (callbacks) {
                var index = callbacks.indexOf(callback);
                if (index >= 0) {
                    var result = callbacks.splice(index, 1)[0];
                    if (callbacks.length === 0)
                        delete events[event];
                    return result;
                }
            }
        }

        function fire (event) {
            var self = this,
                callbacks = events[event];
            if (callbacks)
                callbacks.forEach(function (cbk) {
                    cbk(self);
                });
        }
    }
});