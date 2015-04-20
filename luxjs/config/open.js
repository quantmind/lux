//
//
(function () {

    if (this.lux)
        this.lux = {};

    // The original require
    var require_config = require.config,
        root = this,
        protocol = root.location ? (root.location.protocol === 'file:' ? 'https:' : '') : '',
        end = '.js',
        processed = false,
        ostring = Object.prototype.toString,
        lux = root.lux;


    function isArray(it) {
        return ostring.call(it) === '[object Array]';
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