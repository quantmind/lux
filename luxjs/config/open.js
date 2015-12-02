//
(function (root) {
    "use strict";

    if (!root.lux)
        root.lux = {};

    // If a file assign http as protocol (https does not work with PhantomJS)
    var protocol = root.location ? (root.location.protocol === 'file:' ? 'http:' : '') : '',
        end = '.js',
        ostring = Object.prototype.toString;


    function isString (value) {
        return ostring.call(value) === '[object String]';
    }

    function isArray (value) {
        return ostring.call(value) === '[object Array]';
    }

    function minify () {
        if (root.lux.context)
            return lux.context.MINIFIED_MEDIA;
    }

    function baseUrl () {
        if (root.lux.context)
            return lux.context.MEDIA_URL;
    }

    function extend (o1, o2) {
        if (o2) {
            for (var key in o2) {
                if (o2.hasOwnProperty(key))
                    o1[key] = o2[key];
            }
        }
        return o1;
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
        var decoded = lux.urlBase64Decode(parts[1]);
        if (!decoded) {
            throw new Error('Cannot decode the token');
        }

        return JSON.parse(decoded);
    }


    if (isString(root.lux))
        root.lux = {context: urlBase64DecodeToJSON(root.lux)};

    root.lux.urlBase64Decode = urlBase64Decode;
    root.lux.urlBase64DecodeToJSON = urlBase64DecodeToJSON;
