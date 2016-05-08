import _ from '../ng';

export function noop () {}

const jsLibs = {};


export function getOptions (root, attrs, optionName) {
    var exclude = [name, 'class', 'style'],
        options;

    if (attrs) {
        if (optionName) options = attrs[optionName];
        if (!options) {
            optionName = 'options';
            options = attrs[optionName];
        }
        if (_.isString(options))
            options = getAttribute(root, options);

        if (_.isFunction(options))
            options = options();
    }
    if (!options) options = {};

    if (_.isObject(options))
        _.forEach(attrs, function (value, name) {
            if (name.substring(0, 1) !== '$' && exclude.indexOf(name) === -1)
                options[name] = value;
        });

    return options;
}


export function getAttribute(obj, name) {
    var bits = name.split('.');

    for (var i = 0; i < bits.length; ++i) {
        obj = obj[bits[i]];
        if (!obj) break;
    }
    if (typeof obj === 'function')
        obj = obj();

    return obj;
}


export function urlBase64Decode (str) {
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

export function urlBase64DecodeToJSON (str) {
    var decoded = urlBase64Decode(str);
    if (!decoded) {
        throw new Error('Cannot decode the token');
    }
    return JSON.parse(decoded);
}

export function decodeJWToken (token) {
    var parts = token.split('.');

    if (parts.length !== 3) {
        throw new Error('JWT must have 3 parts');
    }

    return urlBase64DecodeToJSON(parts[1]);
};

export const isAbsolute = new RegExp('^([a-z]+://|//)');


export function joinUrl () {
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
}


export function jsLib(name, callback) {
    var lib = jsLibs[name];

    if (!lib && callback)
        require([name], function (lib) {
            jsLibs[name] = lib;
            callback(lib);
        });

    return lib;
}
