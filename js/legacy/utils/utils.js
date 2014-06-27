    var each = lux.each;

    //  Lux Utils
    //  ------------------------
    
    // Stand alone functions used throughout the lux web libraries.
    
    lux.utils = {
        //
        detector: {
            canvas: !! window.CanvasRenderingContext2D,
            /*
            webgl: (function () {
                try {
                    return !! window.WebGLRenderingContext && !! document.createElement('canvas').getContext('experimental-webgl');
                } catch( e ) {
                    return false;
                }
            }()),
            */
            workers: !! window.Worker,
            fileapi: window.File && window.FileReader && window.FileList && window.Blob
        },
        //
        allClasses: function (elem) {
            var classes = {}, all = [];
            $(elem).each(function() {
                if (this.className) {
                    $.each(this.className.split(' '), function() {
                        var name = this;
                        if (name !== '' && classes[name] === undefined) {
                            classes[name] = name;
                            all.push(name);
                        }
                    });
                }
            });
            return all;
        },
        //
        as_tag: function(tag, elem) {
            var o = $(elem);
            if (!o.length && typeof elem === "string") {
                return $('<'+tag+'>').html(elem);
            }
            if (o.length) {
                if (!o.is(tag)) {
                    o = $('<'+tag+'>').append(o);
                }
                return o;
            }
        },
        //
        closest_color: function (el, property) {
            var val = null;
            el = $(el);
            while (el.length && val === null) {
                el = el.parent();
                val = el.css(property);
                if (val == 'inherit' || val == 'transparent') {
                    val = null;
                }
            }
            return val;
        },
        //
        // Return a valid url from an array of strings. 
        urljoin: function () {
            var normalize = function (str) {
                    return str
                        .replace(/[\/]+/g, '/')
                        .replace(/\/\?/g, '?')
                        .replace(/\/\#/g, '#')
                        .replace(/\:\//g, '://');
                },
                joined = [].slice.call(arguments, 0).join('/');
            return normalize(joined);  
        },
        //
        // Return a uman redable string describing the time ``diff``.
        prettyTime: function (diff) {
            var day_diff = Math.floor(diff / 86400);
            return day_diff === 0 && (
                        diff < 2 && "1 second ago" ||
                        diff < 60 && Math.floor( diff ) + " seconds ago" ||
                        diff < 120 && "1 minute ago" ||
                        diff < 3600 && Math.floor( diff / 60 ) + " minutes ago" ||
                        diff < 7200 && "1 hour ago" ||
                        diff < 86400 && Math.floor( diff / 3600 ) + " hours ago") ||
                    day_diff === 1 && "Yesterday" ||
                    day_diff < 7 && day_diff + " days ago" ||
                    day_diff < 31 && Math.ceil( day_diff / 7 ) + " weeks ago";
        },
        //
        asDate: function (value) {
            if (value instanceof Date) {
                return value;
            } else {
                var d = parseFloat(value);
                if (d === d) {
                    return new Date(1000*d);
                } else {
                    throw new TypeError('Could not convert ' + value + ' to a date');
                }
            }
        }
    };