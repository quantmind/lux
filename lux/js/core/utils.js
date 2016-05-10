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
}

export function jsLib(name, callback) {
    var lib = jsLibs[name];

    if (callback) {
        if (lib)
            callback(lib);
        else {
            require([name], function (lib) {
                jsLibs[name] = lib || true;
                callback(lib);
            });
        }
    }

    return lib;
}


export function LuxException (value, message) {
   this.value = value;
   this.message = message;

   this.toString = function() {
      return `${this.message} : ${this.value}`;
   };
}
