/* eslint-plugin-disable angular */
define([], function () {
    'use strict';

    var root = window,
        lux = root.lux || {},
        ostring = Object.prototype.toString;

    if (isString(lux))
        lux = {context: urlBase64DecodeToJSON(lux)};

    root.lux = lux;

    lux.root = root;
    lux.require = extend(lux.require);
    lux.extend = extend;
    lux.isString = isString;
    lux.isArray = isArray;
    lux.isObject = isObject;
    lux.urlBase64Decode = urlBase64Decode;
    lux.urlBase64DecodeToJSON = urlBase64DecodeToJSON;

    return lux;

    function extend (o1, o2) {
        if (!o1) o1 = {};
        if (o2) {
            for (var key in o2) {
                if (o2.hasOwnProperty(key))
                    o1[key] = o2[key];
            }
        }
        return o1;
    }

    function isString (value) {
        return ostring.call(value) === '[object String]';
    }

    function isArray (value) {
        return ostring.call(value) === '[object Array]';
    }

    function isObject (value) {
        return ostring.call(value) === '[object Object]';
    }

    function urlBase64Decode (str) {
        var output = str.replace('-', '+').replace('_', '/');
        switch (output.length % 4) {
            case 0: { break; }
            case 2: { output += '=='; break; }
            case 3: { output += '='; break; }
            default: {
                throw 'Illegal base64url string!';
            }
        }
        //polifyll https://github.com/davidchambers/Base64.js
        return decodeURIComponent(escape(window.atob(output)));
    }

    function urlBase64DecodeToJSON (str) {
        var decoded = urlBase64Decode(str);
        if (!decoded) {
            throw new Error('Cannot decode the token');
        }
        return JSON.parse(decoded);
    }

});
