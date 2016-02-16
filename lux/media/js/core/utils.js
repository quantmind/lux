/* eslint-plugin-disable angular */
define(['angular',
        'lux/config/main'], function (angular, lux) {
    'use strict';

    var root = lux.root,
        forEach = angular.forEach,
        slice = Array.prototype.slice,
        generateCallbacks = function () {
            var callbackFunctions = [],
                callFunctions = function () {
                    var self = this,
                        args = slice.call(arguments, 0);
                    callbackFunctions.forEach(function (f) {
                        f.apply(self, args);
                    });
                };
            //
            callFunctions.add = function (f) {
                callbackFunctions.push(f);
            };
            return callFunctions;
        };
    //
    // Add a callback for an event to an element
    lux.addEvent = function (element, event, callback) {
        var handler = element[event];
        if (!handler)
            element[event] = handler = generateCallbacks();
        if (handler.add)
            handler.add(callback);
    };
    //
    lux.windowResize = function (callback) {
        lux.addEvent(window, 'onresize', callback);
    };
    //
    lux.windowHeight = function () {
        return window.innerHeight > 0 ? window.innerHeight : screen.availHeight;
    };
    //
    lux.isAbsolute = new RegExp('^([a-z]+://|//)');
    //
    // Check if element has tagName tag
    lux.isTag = function (element, tag) {
        element = angular.element(element);
        return element.length === 1 && element[0].tagName === tag.toUpperCase();
    };
    //
    lux.joinUrl = function () {
        var bit, url = '';
        for (var i = 0; i < arguments.length; ++i) {
            bit = arguments[i];
            if (bit) {
                var cbit = bit,
                    slash = false;
                // remove front slashes if cbit has some
                while (url && cbit.substring(0, 1) === '/')
                    cbit = cbit.substring(1);
                // remove end slashes
                while (cbit.substring(cbit.length - 1) === '/') {
                    slash = true;
                    cbit = cbit.substring(0, cbit.length - 1);
                }
                if (cbit) {
                    if (url && url.substring(url.length - 1) !== '/')
                        url += '/';
                    url += cbit;
                    if (slash)
                        url += '/';
                }
            }
        }
        return url;
    };
    //
    //  getOPtions
    //  ===============
    //
    //  Retrive options for the ``options`` string in ``attrs`` if available.
    //  Used by directive when needing to specify options in javascript rather
    //  than html data attributes.
    lux.getOptions = function (attrs, optionName) {
        var options;
        if (attrs) {
            if (optionName) options = attrs[optionName];
            if (!options) {
                optionName = 'options';
                options = attrs[optionName];
            }
            if (angular.isString(options))
                options = getAttribute(root, options);
            if (angular.isFunction(options))
                options = options();
        }
        if (!options) options = {};
        if (lux.isObject(options))
            angular.forEach(attrs, function (value, name) {
                if (name.substring(0, 1) !== '$' && name !== optionName)
                    options[name] = value;
            });

        return options;
    };
    //
    // random generated numbers for a uuid
    lux.s4 = function () {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    };
    //
    // Extend the initial array with values for other arrays
    lux.extendArray = function () {
        if (!arguments.length) return;
        var value = arguments[0],
            push = function (v) {
                value.push(v);
            };
        if (typeof(value.push) === 'function') {
            for (var i = 1; i < arguments.length; ++i)
                forEach(arguments[i], push);
        }
        return value;
    };
    //
    //  querySelector
    //  ===================
    //
    //  Simple wrapper for a querySelector
    lux.querySelector = function (elem, query) {
        if (arguments.length === 1 && lux.isString(elem)) {
            query = elem;
            elem = document;
        }
        elem = angular.element(elem);
        if (elem.length && query)
            return angular.element(elem[0].querySelector(query));
        else
            return elem;
    };
    //
    //    LoadCss
    //  =======================
    //
    //  Load a style sheet link
    var loadedCss = {};
    //
    lux.loadCss = function (filename) {
        if (!loadedCss[filename]) {
            loadedCss[filename] = true;
            var fileref = document.createElement('link');
            fileref.setAttribute('rel', 'stylesheet');
            fileref.setAttribute('type', 'text/css');
            fileref.setAttribute('href', filename);
            document.getElementsByTagName('head')[0].appendChild(fileref);
        }
    };
    //
    //
    lux.globalEval = function (data) {
        if (data) {
            // We use execScript on Internet Explorer
            // We use an anonymous function so that context is window
            // rather than jQuery in Firefox
            (root.execScript || function (data) {
                root['eval'].call(root, data);
            })(data);
        }
    };
    //
    // Simple Slugify function
    lux.slugify = function (str) {
        str = str.replace(/^\s+|\s+$/g, ''); // trim
        str = str.toLowerCase();

        // remove accents, swap ñ for n, etc
        var from = 'àáäâèéëêìíïîòóöôùúüûñç·/_,:;';
        var to = 'aaaaeeeeiiiioooouuuunc------';
        for (var i = 0, l = from.length; i < l; i++) {
            str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
        }

        str = str.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
            .replace(/\s+/g, '-') // collapse whitespace and replace by -
            .replace(/-+/g, '-'); // collapse dashes

        return str;
    };
    //
    lux.now = function () {
        return Date.now ? Date.now() : new Date().getTime();
    };
//
    lux.size = function (o) {
        if (!o) return 0;
        if (o.length !== undefined) return o.length;
        var n = 0;
        forEach(o, function () {
            ++n;
        });
        return n;
    };
    //
    // Used by the getObject function
    function getAttribute (obj, name) {
        var bits = name.split('.');

        for (var i = 0; i < bits.length; ++i) {
            obj = obj[bits[i]];
            if (!obj) break;
        }
        if (typeof obj === 'function')
            obj = obj();

        return obj;
    }
    //
    //
    //  Get Options
    //  ==============================================
    //
    //  Obtain an object from scope (if available) with fallback to
    //  the global javascript object
    lux.getObject = function (attrs, name, scope) {
        var key = attrs[name],
            exclude = [name, 'class', 'style'],
            options;

        if (key) {
            // Try the scope first
            if (scope) options = getAttribute(scope, key);

            if (!options) options = getAttribute(root, key);
        }
        if (!options) options = {};

        forEach(attrs, function (value, name) {
            if (name.substring(0, 1) !== '$' && exclude.indexOf(name) === -1)
                options[name] = value;
        });
        return options;
    };

    /**
     * Formats a string (using simple substitution)
     * @param   {String}    str         e.g. 'Hello {name}!'
     * @param   {Object}    values      e.g. {name: 'King George III'}
     * @returns {String}                e.g. 'Hello King George III!'
     */
    lux.formatString = function (str, values) {
        return str.replace(/{(\w+)}/g, function (match, placeholder) {
            return values.hasOwnProperty(placeholder) ? values[placeholder] : '';
        });
    };
    //
    //  Capitalize the first letter of string
    lux.capitalize = function (str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    };

    /**
     * Obtain a JSON object from a string (if available) otherwise null
     *
     * @param {string}
     * @returns {object} json object
     */
    lux.getJsonOrNone = function (str) {
        try {
            return JSON.parse(str);
        } catch (error) {
            return null;
        }
    };

    /**
     * Checks if a JSON value can be stringify
     *
     * @param {value} json value
     * @returns {boolean}
     */
    lux.isJsonStringify = function (value) {
        if (lux.isObject(value) || lux.isArray(value) || lux.isString(value))
            return true;
        return false;
    };

    // Hack for delaying with ui-router state.href
    // TODO: fix this!
    lux.stateHref = function (state, State, Params) {
        if (Params) {
            var url = state.href(State, Params);
            return url.replace(/%2F/g, '/');
        } else {
            return state.href(State);
        }
    };

    return lux;
});
