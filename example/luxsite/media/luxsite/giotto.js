//      GiottoJS - v0.2.0
//
//      Compiled 2015-05-17.
//
//      Copyright (c) 2014 - 2015 - Luca Sbardella
//      All rights reserved.
//
//      Licensed BSD.
//      For all details and documentation:
//      http://giottojs.org
//
(function (factory) {
    var root;
    if (typeof module === "object" && module.exports)
        root = module.exports;
    else
        root = window;
    //
    if (typeof define === 'function' && define.amd) {
        // Support AMD. Register as an anonymous module.
        // NOTE: List all dependencies in AMD style
        define(['d3'], function () {
            return factory(d3, root);
        });
    } else if (typeof module === "object" && module.exports) {
        // No AMD. Set module as a global variable
        // NOTE: Pass dependencies to factory function
        // (assume that d3 is also global.)
        factory(d3, root);
    }
}(function(d3, root) {
    //"use strict";
    var giotto = {
            version: "0.2.0",
            d3: d3,
            math: {},
            svg: {},
            canvas: {},
            geo: {},
            data: {}
        },
        g = giotto,
        theme = root.giottoTheme || 'light';

    d3.giotto = giotto;
    d3.canvas = {};


    //  D3 internal functions
    //  =======================================================================
    //
    //  Used by GiottoJS, mainly by the canvas module
    //  These are copied from d3.js

    //  Copyright (c) 2010-2015, Michael Bostock
    //  All rights reserved.

    function d3_identity(d) {
        return d;
    }

    function d3_zero() {
        return 0;
    }

    function d3_functor (v) {
        return typeof v === "function" ? v : function() {
            return v;
        };
    }

    function d3_scaleExtent(domain) {
        var start = domain[0], stop = domain[domain.length - 1];
        return start < stop ? [ start, stop ] : [ stop, start ];
    }

    function d3_scaleRange(scale) {
        return scale.rangeExtent ? scale.rangeExtent() : d3_scaleExtent(scale.range());
    }

    function d3_geom_pointX(d) {
        return d[0];
    }

    function d3_geom_pointY(d) {
        return d[1];
    }

    function d3_true() {
        return true;
    }

    // Matrix to transform basis (b-spline) control points to bezier
    // control points. Derived from FvD 11.2.8.
    var d3_svg_lineBasisBezier1 = [0, 2/3, 1/3, 0],
        d3_svg_lineBasisBezier2 = [0, 1/3, 2/3, 0],
        d3_svg_lineBasisBezier3 = [0, 1/6, 2/3, 1/6];

    // Computes the slope from points p0 to p1.
    function d3_svg_lineSlope(p0, p1) {
        return (p1[1] - p0[1]) / (p1[0] - p0[0]);
    }

    // Returns the dot product of the given four-element vectors.
    function d3_svg_lineDot4(a, b) {
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
    }

    // Generates tangents for a cardinal spline.
    function d3_svg_lineCardinalTangents(points, tension) {
        var tangents = [],
            a = (1 - tension) / 2,
            p0,
            p1 = points[0],
            p2 = points[1],
            i = 1,
            n = points.length;
        while (++i < n) {
            p0 = p1;
            p1 = p2;
            p2 = points[i];
            tangents.push([a * (p2[0] - p0[0]), a * (p2[1] - p0[1])]);
        }
        return tangents;
    }

    // Compute three-point differences for the given points.
    // http://en.wikipedia.org/wiki/Cubic_Hermite_spline#Finite_difference
    function d3_svg_lineFiniteDifferences(points) {
        var i = 0,
          j = points.length - 1,
          m = [],
          p0 = points[0],
          p1 = points[1],
          d = m[0] = d3_svg_lineSlope(p0, p1);
        while (++i < j) {
            m[i] = (d + (d = d3_svg_lineSlope(p0 = p1, p1 = points[i + 1]))) / 2;
        }
        m[i] = d;
        return m;
    }

    // Interpolates the given points using Fritsch-Carlson Monotone cubic Hermite
    // interpolation. Returns an array of tangent vectors. For details, see
    // http://en.wikipedia.org/wiki/Monotone_cubic_interpolation
    function d3_svg_lineMonotoneTangents(points) {
        var tangents = [],
          d,
          a,
          b,
          s,
          m = d3_svg_lineFiniteDifferences(points),
          i = -1,
          j = points.length - 1;

        // The first two steps are done by computing finite-differences:
        // 1. Compute the slopes of the secant lines between successive points.
        // 2. Initialize the tangents at every point as the average of the secants.

        // Then, for each segment…
        while (++i < j) {
            d = d3_svg_lineSlope(points[i], points[i + 1]);

            // 3. If two successive yk = y{k + 1} are equal (i.e., d is zero), then set
            // mk = m{k + 1} = 0 as the spline connecting these points must be flat to
            // preserve monotonicity. Ignore step 4 and 5 for those k.

            if (abs(d) < ε) {
                m[i] = m[i + 1] = 0;
            } else {
                // 4. Let ak = mk / dk and bk = m{k + 1} / dk.
                a = m[i] / d;
                b = m[i + 1] / d;

                // 5. Prevent overshoot and ensure monotonicity by restricting the
                // magnitude of vector <ak, bk> to a circle of radius 3.
                s = a * a + b * b;
                if (s > 9) {
                    s = d * 3 / Math.sqrt(s);
                    m[i] = s * a;
                    m[i + 1] = s * b;
                }
            }
        }

        // Compute the normalized tangent vector from the slopes. Note that if x is
        // not monotonic, it's possible that the slope will be infinite, so we protect
        // against NaN by setting the coordinate to zero.
        i = -1; while (++i <= j) {
            s = (points[Math.min(j, i + 1)][0] - points[Math.max(0, i - 1)][0]) / (6 * (1 + m[i] * m[i]));
            tangents.push([s || 0, m[i] * s || 0]);
        }

        return tangents;
    }

    function d3_geom_polygonIntersect(c, d, a, b) {
        var x1 = c[0], x3 = a[0], x21 = d[0] - x1, x43 = b[0] - x3, y1 = c[1], y3 = a[1], y21 = d[1] - y1, y43 = b[1] - y3, ua = (x43 * (y1 - y3) - y43 * (x1 - x3)) / (y43 * x21 - x43 * y21);
        return [ x1 + ua * x21, y1 + ua * y21 ];
    }

    function d3_asin(x) {
        return x > 1 ? halfπ : x < -1 ? -halfπ : Math.asin(x);
    }

    // ARCS

    var d3_svg_arcAuto = "auto";

    function d3_svg_arcInnerRadius(d) {
        return d.innerRadius;
    }

    function d3_svg_arcOuterRadius(d) {
        return d.outerRadius;
    }

    function d3_svg_arcStartAngle(d) {
        return d.startAngle;
    }

    function d3_svg_arcEndAngle(d) {
        return d.endAngle;
    }

    function d3_svg_arcPadAngle(d) {
        return d && d.padAngle;
    }

    // Note: similar to d3_cross2d, d3_geom_polygonInside
    function d3_svg_arcSweep(x0, y0, x1, y1) {
        return (x0 - x1) * y0 - (y0 - y1) * x0 > 0 ? 0 : 1;
    }

    // Compute perpendicular offset line of length rc.
    // http://mathworld.wolfram.com/Circle-LineIntersection.html
    function d3_svg_arcCornerTangents(p0, p1, r1, rc, cw) {
        var x01 = p0[0] - p1[0],
            y01 = p0[1] - p1[1],
            lo = (cw ? rc : -rc) / Math.sqrt(x01 * x01 + y01 * y01),
            ox = lo * y01,
            oy = -lo * x01,
            x1 = p0[0] + ox,
            y1 = p0[1] + oy,
            x2 = p1[0] + ox,
            y2 = p1[1] + oy,
            x3 = (x1 + x2) / 2,
            y3 = (y1 + y2) / 2,
            dx = x2 - x1,
            dy = y2 - y1,
            d2 = dx * dx + dy * dy,
            r = r1 - rc,
            D = x1 * y2 - x2 * y1,
            d = (dy < 0 ? -1 : 1) * Math.sqrt(r * r * d2 - D * D),
            cx0 = (D * dy - dx * d) / d2,
            cy0 = (-D * dx - dy * d) / d2,
            cx1 = (D * dy + dx * d) / d2,
            cy1 = (-D * dx + dy * d) / d2,
            dx0 = cx0 - x3,
            dy0 = cy0 - y3,
            dx1 = cx1 - x3,
            dy1 = cy1 - y3;

        // Pick the closer of the two intersection points.
        // TODO Is there a faster way to determine which intersection to use?
        if (dx0 * dx0 + dy0 * dy0 > dx1 * dx1 + dy1 * dy1) cx0 = cx1, cy0 = cy1;

        return [
            [cx0 - ox, cy0 - oy],
            [cx0 * r1 / r, cy0 * r1 / r]
        ];
    }

    var d3_svg_brushCursor = {
        n: "ns-resize",
        e: "ew-resize",
        s: "ns-resize",
        w: "ew-resize",
        nw: "nwse-resize",
        ne: "nesw-resize",
        se: "nwse-resize",
        sw: "nesw-resize"
    };

    var d3_svg_brushResizes = [
      ["n", "e", "s", "w", "nw", "ne", "se", "sw"],
      ["e", "w"],
      ["n", "s"],
      []
    ];

    //  END of D3 internal functions
    //  =======================================================================


    /** @module data */

    // Convert an array of array obtained from reading a CSV file into an array of objects
    g.data.fromcsv = function (data) {
        var labels = data[0],
            rows = [],
            o, j;
        for (var i=1; i<data.length; ++i) {
            o = {};
            for (j=0; j<labels.length; ++j)
                o[labels[j]] = data[i][j];
            rows.push(o);
        }
        return rows;
    };

    //  Giotto serie
    //  =================
    //
    //  A serie is an abstraction on top of an array.
    //  It provides accessor functions and several utilities for
    //  understanding and manipulating the underlying data which is either
    //  an array or another serie.
    g.data.serie = function () {
        var serie = {},
            x = d3_geom_pointX,
            y = d3_geom_pointY,
            data,
            label;

        serie.x = function (_) {
            if (!arguments.length) return x;
            if (!isFunction(_)) _ = label_functor(_);
            x = _;
            return serie;
        };

        serie.y = function (_) {
            if (!arguments.length) return y;
            if (!isFunction(_)) _ = label_functor(_);
            y = _;
            return serie;
        };

        serie.label = function (_) {
            if (!arguments.length) return label;
            if (_ && !isFunction(_)) _ = label_functor(_);
            label = _;
            return serie;
        };

        //  Set/get data associated with this serie
        serie.data = function (_) {
            if (!arguments.length) return data;
            data = _;
            return serie;
        };

        serie.forEach = function (callback) {
            if (data)
                data.forEach(callback);
            return serie;
        };

        serie.map = function (callback) {
            if (data)
                return data.map(callback);
        };

        //  Get a value at key
        //  the data must implement the get function
        serie.get = function (key) {
            if (data && isFunction(data.get))
                return data.get(key);
        };

        serie.xrange = function () {
            return getRange(x);
        };

        serie.yrange = function () {
            return getRange(y);
        };

        Object.defineProperty(serie, 'length', {
            get: function () {
                return data ? data.length : 0;
            }
        });

        return serie;

        //  Get a valid range for this timeserie if possible
        //  If a valid range is available is return as an array [min, max]
        //  otherwise nothing is returned
        function getRange (accessor) {
            var vmin = Infinity,
                vmax =-Infinity,
                ordinal = false,
                val;

            if (!data) return;

            data.forEach(function (d) {
                val = accessor(d);
                if (!isDate(val))
                    val = +val;

                if (isNaN(val))
                    ordinal = true;
                else {
                    vmin = val < vmin ? val : vmin;
                    vmax = val > vmax ? val : vmax;
                }
            });

            if (!ordinal) return [vmin, vmax];
        }
    };

    g.serie = g.data.serie;
    //
    //  Build a multivariate data handler
    //
    //  data is an array of objects (records)
    g.data.multi = function () {
        var multi = g.data.serie(),
            keys;

        multi.key = function (key) {
            if (key && !isFunction(key)) key = label_functor(key);
            var data = multi.data();
            keys = null;
            if (key && data) {
                keys = {};
                data.forEach(function (d) {
                    keys[key(d)] = d;
                });
            }
            return multi;
        };

        // retrieve a record by key
        multi.get = function (key) {
            if (keys)
                return keys[key];
        };

        //  Build a single variate serie from this multi-variate serie
        multi.serie = function () {
            var label = multi.label();
            return g.data.serie()
                         .data(multi)
                         .label(label)
                         .x(multi.x() || label)
                         .y(multi.y());
        };

        return multi;
    };

    g.multi = g.data.multi;


    function label_functor (label) {
        return function (d) {
            return d[label];
        };
    }
    function noop () {}

    var log = function (debug) {

        function formatError(arg) {
            if (arg instanceof Error) {
                if (arg.stack) {
                    arg = (arg.message && arg.stack.indexOf(arg.message) === -1
                        ) ? 'Error: ' + arg.message + '\n' + arg.stack : arg.stack;
                } else if (arg.sourceURL) {
                    arg = arg.message + '\n' + arg.sourceURL + ':' + arg.line;
                }
            }
            return arg;
        }

        function consoleLog(type) {
            var console = window.console || {},
                logFn = console[type] || console.log || noop,
                hasApply = false;

              // Note: reading logFn.apply throws an error in IE11 in IE8 document mode.
              // The reason behind this is that console.log has type "object" in IE8...
              try {
                    hasApply = !!logFn.apply;
              } catch (e) {}

              if (hasApply) {
                    return function() {
                        var args = [];
                        for(var i=0; i<arguments.length; ++i)
                            args.push(formatError(arguments[i]));
                        return logFn.apply(console, args);
                    };
            }

            // we are IE which either doesn't have window.console => this is noop and we do nothing,
            // or we are IE where console.log doesn't have apply so we log at least first 2 args
            return function(arg1, arg2) {
                logFn(arg1, arg2 === null ? '' : arg2);
            };
        }

        return {
            log: consoleLog('log'),
            info: consoleLog('info'),
            warn: consoleLog('warn'),
            error: consoleLog('error'),
            debug: (function () {
                var fn = consoleLog('debug');

                return function() {
                    if (debug) {
                        fn.apply(self, arguments);
                    }
                };
            }()),

        };
    };

    g.log = log(root.debug);


    var
    //
    ostring = Object.prototype.toString,
    //
    // Underscore-like object
    _ = g._ = {},
    //  Simple extend function
    //
    extend = g.extend = _.extend = function () {
        var length = arguments.length,
            object = arguments[0],
            index = 0,
            deep = false,
            obj;

        if (object === true) {
            deep = true;
            object = arguments[1];
            index++;
        }

        if (!object || length < index + 2)
            return object;

        while (++index < length) {
            obj = arguments[index];
            if (Object(obj) === obj) {
                for (var prop in obj) {
                    if (obj.hasOwnProperty(prop)) {
                        if (deep) {
                            if (isObject(obj[prop]))
                                if (isObject(object[prop]))
                                    extend(true, object[prop], obj[prop]);
                                else
                                    object[prop] = extend(true, {}, obj[prop]);
                            else
                                object[prop] = obj[prop];
                        } else
                            object[prop] = obj[prop];
                    }
                }
            }
        }
        return object;
    },
    //  copyMissing
    //  =================
    //
    //  Copy values to toObj from fromObj which are missing (undefined) in toObj
    copyMissing = _.copyMissing = function (fromObj, toObj, deep) {
        if (fromObj && toObj) {
            var v, t;
            for (var prop in fromObj) {
                if (fromObj.hasOwnProperty(prop)) {
                    t = fromObj[prop];
                    v = toObj[prop];
                    if (deep && isObject(t) && t !== v) {
                        if (!isObject(v)) v = {};
                        copyMissing(t, v, deep);
                        toObj[prop] = v;
                    } else if (v === undefined) {
                        toObj[prop] = t;
                    }
                }
            }
        }
        return toObj;
    },
    //
    getRootAttribute = function (name) {
        var obj = root,
            bits= name.split('.');

        for (var i=0; i<bits.length; ++i) {
            obj = obj[bits[i]];
            if (!obj) break;
        }
        return obj;
    },
    //
    //
    keys = _.keys = function (obj) {
        var keys = [];
        for (var key in obj) {
            if (obj.hasOwnProperty(key))
                keys.push(key);
        }
        return keys;
    },

    size = _.size = function (obj) {
        if (!obj)
            return 0;
        else if (obj.length !== undefined)
            return obj.length;
        else if (_.isObject(obj)) {
            var n = 0;
            for (var key in obj)
                if (obj.hasOwnProperty(key)) n++;
            return n;
        }
        else
            return 0;
    },
    //
    forEach = _.forEach = _.each = function (obj, callback) {
        if (!obj) return;
        if (obj.forEach) return obj.forEach(callback);
        for (var key in obj) {
            if (obj.hasOwnProperty(key))
                callback(obj[key], key);
        }
    },
    //
    pick = _.pick = function (obj, callback) {
        var picked = {},
            val;
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
                val = callback(obj[key], key);
                if (val !== undefined)
                    picked[key] = val;
            }
        }
        return picked;
    },

    // Extend the initial array with values for other arrays
    extendArray = _.extendArray = function () {
        if (!arguments.length) return;
        var value = arguments[0],
            push = function (v) {
                value.push(v);
            };
        if (typeof(value.push) === 'function') {
            for (var i=1; i<arguments.length; ++i)
                forEach(arguments[i], push);
        }
        return value;
    },

    //
    isObject = _.isObject = function (value) {
        return ostring.call(value) === '[object Object]';
    },
    //
    isString = _.isString = function (value) {
        return ostring.call(value) === '[object String]';
    },
    //
    isFunction = _.isFunction = function (value) {
        return ostring.call(value) === '[object Function]';
    },
    //
    isArray = _.isArray = function (value) {
        return ostring.call(value) === '[object Array]';
    },
    //
    isDate = _.isDate = function (value) {
        return ostring.call(value) === '[object Date]';
    },
    //
    isNull = _.isNull = function (value) {
        return value === undefined || value === null;
    },

    encodeObject = _.encodeObject = function (obj, contentType) {
        var p;
        if (contentType === 'multipart/form-data') {
            var fd = new FormData();
            for(p in obj)
                if (obj.hasOwnProperty(p))
                    fd.append(p, obj[p]);
            return fd;
        } else if (contentType === 'application/json') {
            return JSON.stringify(obj);
        } else {
            var str = [];
            for(p in obj)
                if (obj.hasOwnProperty(p))
                    str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
            return str.join("&");
        }
    },

    getObject = _.getObject = function (o) {
        if (_.isString(o)) {
            var bits= o.split('.');
            o = root;

            for (var i=0; i<bits.length; ++i) {
                o = o[bits[i]];
                if (!o) break;
            }
        }
        return o;
    },

    //  Load a style sheet link
    loadCss = _.loadCss = function (filename) {
        var fileref = document.createElement("link");
        fileref.setAttribute("rel", "stylesheet");
        fileref.setAttribute("type", "text/css");
        fileref.setAttribute("href", filename);
        document.getElementsByTagName("head")[0].appendChild(fileref);
    },

    addCss = _.addCss = function (base, obj) {
        var css = [];

        accumulate(base, obj);

        if (css.length) {
            css = css.join('\n');
            var style = document.createElement("style");
            style.innerHTML = css;
            document.getElementsByTagName("head")[0].appendChild(style);
            return style;
        }

        function accumulate (s, o) {
            var bits = [],
                v;
            for (var p in o)
                if (o.hasOwnProperty(p)) {
                    v = o[p];
                    if (_.isObject(v))
                        accumulate(s + ' .' + p, v);
                    else
                        bits.push('    ' + p + ': ' + v + ';');
                }
            if (bits.length)
                css.push(s + ' {\n' + bits.join('\n') + '\n}');
        }
    },

        // Simple Slugify function
    slugify = _.slugify = function (str) {
        str = str.replace(/^\s+|\s+$/g, ''); // trim
        str = str.toLowerCase();

        // remove accents, swap ñ for n, etc
        var from = "àáäâèéëêìíïîòóöôùúüûñç·/_,:;";
        var to   = "aaaaeeeeiiiioooouuuunc------";
        for (var i=0, l=from.length ; i<l ; i++) {
            str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
        }

        str = str.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
            .replace(/\s+/g, '-') // collapse whitespace and replace by -
            .replace(/-+/g, '-'); // collapse dashes

        return str;
    },

    fontstrings = ['style', 'variant', 'weight', 'size', 'family'],

    fontString = _.fontString = function (opts) {
        var bits = [],
            v;
        for (var i=0; i<fontstrings.length; ++i) {
            v = opts[fontstrings[i]];
            if (v)
                bits.push(v);
        }
        return bits.join(' ');
    },
    //
    now = _.now = function () {
        return Date.now ? Date.now() : new Date().getTime();
    };



    function giotto_id (element) {
        var id = element ? element.attr('id') : null;
        if (!id) {
            id = 'giotto' + (++_idCounter);
            if (element) element.attr('id', id);
        }
        return id;
    }

    function svg_defs (element) {
        var svg = d3.select(getSVGNode(element.node())),
            defs = svg.select('defs');
        if (!defs.size())
            defs = svg.append('defs');
        return defs;
    }

    function getWidth (element) {
        return getParentRectValue(element, 'width');
    }

    function getHeight (element) {
        return getParentRectValue(element, 'height');
    }

    function getWidthElement (element) {
        return getParentElementRect(element, 'width');
    }

    function getHeightElement (element) {
        return getParentElementRect(element, 'height');
    }

    function getParentRectValue (element, key) {
        var parent = element.node ? element.node() : element,
            r, v;
        while (parent && parent.tagName !== 'BODY') {
            v = parent.getBoundingClientRect()[key];
            if (v)
                break;
            parent = parent.parentNode;
        }
        return v;
    }

    function getParentElementRect (element, key) {
        var parent = element.node ? element.node() : element,
            r, v;
        while (parent && parent.tagName !== 'BODY') {
            v = parent.getBoundingClientRect()[key];
            if (v)
                return d3.select(parent);
            parent = parent.parentNode;
        }
    }

    function getSVGNode (el) {
        if(el.tagName.toLowerCase() === 'svg')
            return el;

        return el.ownerSVGElement;
    }

    // Given a shape on the screen, will return an SVGPoint for the directions
    // n(north), s(south), e(east), w(west), ne(northeast), se(southeast), nw(northwest),
    // sw(southwest).
    //
    //    +-+-+
    //    |   |
    //    +   +
    //    |   |
    //    +-+-+
    //
    // Returns an Object {x, y, e, w, nw, sw, ne, se}
    function getScreenBBox (target) {

        var bbox = {},
            matrix = target.getScreenCTM(),
            svg = getSVGNode(target),
            point = svg.createSVGPoint(),
            tbbox = target.getBBox(),
            width = tbbox.width,
            height = tbbox.height;

        point.x = tbbox.x;
        point.y = tbbox.y;
        bbox.nw = point.matrixTransform(matrix);
        point.x += width;
        bbox.ne = point.matrixTransform(matrix);
        point.y += height;
        bbox.se = point.matrixTransform(matrix);
        point.x -= width;
        bbox.sw = point.matrixTransform(matrix);
        point.y -= 0.5*height;
        bbox.w = point.matrixTransform(matrix);
        point.x += width;
        bbox.e = point.matrixTransform(matrix);
        point.x -= 0.5*width;
        point.y -= 0.5*height;
        bbox.n = point.matrixTransform(matrix);
        point.y += height;
        bbox.s = point.matrixTransform(matrix);

        return bbox;
    }


    g.math.distances = {

        euclidean: function(v1, v2) {
            var total = 0;
            for (var i = 0; i < v1.length; i++) {
                total += Math.pow(v2[i] - v1[i], 2);
            }
            return Math.sqrt(total);
        }
    };
    //
    //  K-means clustering
    g.math.kmeans = function (centroids, max_iter, distance) {
        var km = {};

        max_iter = max_iter || 300;
        distance = distance || "euclidean";
        if (typeof distance == "string")
            distance = g.math.distances[distance];

        km.centroids = function (x) {
            if (!arguments.length) return centroids;
            centroids = x;
            return km;
        };

        km.maxIters = function (x) {
            if (!arguments.length) return max_iter;
            max_iter = +x;
            return km;
        };

        // create a set of random centroids from a set of points
        km.randomCentroids = function (points, K) {
            var means = points.slice(0); // copy
            means.sort(function() {
                return Math.round(Math.random()) - 0.5;
            });
            return means.slice(0, K);
        };

        km.classify = function (point) {
            var min = Infinity,
                index = 0,
                i, dist;
            for (i = 0; i < centroids.length; i++) {
                dist = distance(point, centroids[i]);
                if (dist < min) {
                    min = dist;
                    index = i;
                }
           }
           return index;
        };

        km.cluster = function (points, callback) {

            var iterations = 0,
                movement = true,
                N = points.length,
                K = centroids.length,
                clusters = new Array(K),
                newCentroids,
                n, k;

            if (N < K)
                throw Error('Number of points less than the number of clusters in K-means classification');

            while (movement && iterations < max_iter) {
                movement = false;
                ++iterations;

                // Assignments
                for (k = 0; k < K; ++k)
                    clusters[k] = {centroid: centroids[k], points: [], indices: []};

                for (n = 0; n < N; n++) {
                    k = km.classify(points[n]);
                    clusters[k].points.push(points[n]);
                    clusters[k].indices.push(n);
                }

                // Update centroids
                newCentroids = [];
                for (k = 0; k < K; ++k) {
                    if (clusters[k].points.length)
                        newCentroids.push(g.math.mean(clusters[k].points));
                    else {
                        // A centroid with no points, randomly re-initialise it
                        newCentroids = km.randomCentroids(points, K);
                        break;
                    }
                }

                for (k = 0; k < K; ++k) {
                    if (newCentroids[k] != centroids[k]) {
                        centroids = newCentroids;
                        movement = true;
                        break;
                    }
                }

                if (callback)
                    callback(clusters, iterations);
            }

            return clusters;
        };

        return km;
    };
    var ε = 1e-6,
        ε2 = ε * ε,
        π = Math.PI,
        τ = 2 * π,
        τε = τ - ε,
        halfπ = π / 2,
        d3_radians = π / 180,
        d3_degrees = 180 / π,
        abs = Math.abs;

    g.math.xyfunction = function (X, funy) {
        var xy = [];
        if (isArray(X))
            X.forEach(function (x) {
                xy.push([x, funy(x)]);
            });
        return xy;
    };

    // The arithmetic average of a array of points
    g.math.mean = function (points) {
        var mean = points[0].slice(0), // copy the first point
            point, i, j;
        for (i=1; i<points.length; ++i) {
            point = points[i];
            for (j=0; j<mean.length; ++j)
                mean[j] += point[j];
        }
        for (j=0; j<mean.length; ++j)
            mean[j] /= points.length;
        return mean;
    };
    var BITS = 52,
        SCALE = 2 << 51,
        MAX_DIMENSION = 21201,
        COEFFICIENTS = [
            'd       s       a       m_i',
            '2       1       0       1',
            '3       2       1       1 3',
            '4       3       1       1 3 1',
            '5       3       2       1 1 1',
            '6       4       1       1 1 3 3',
            '7       4       4       1 3 5 13',
            '8       5       2       1 1 5 5 17',
            '9       5       4       1 1 5 5 5',
            '10      5       7       1 1 7 11 1'
        ];


    g.math.sobol = function (dim) {
        if (dim < 1 || dim > MAX_DIMENSION) throw new Error("Out of range dimension");
        var sobol = {},
            count = 0,
            direction = [],
            x = [],
            zero = [],
            lines,
            i;

        sobol.next = function() {
            var v = [];
            if (count === 0) {
                count++;
                return zero.slice();
            }
            var c = 1;
            var value = count - 1;
            while ((value & 1) == 1) {
                value >>= 1;
                c++;
            }
            for (i = 0; i < dim; i++) {
                x[i] ^= direction[i][c];
                v[i] = x[i] / SCALE;
            }
            count++;
            return v;
        };

        sobol.dimension = function () {
            return dim;
        };

        sobol.count = function () {
            return count;
        };


        var tmp = [];
        for (i = 0; i <= BITS; i++) tmp.push(0);
        for (i = 0; i < dim; i++) {
            direction[i] = tmp.slice();
            x[i] = 0;
            zero[i] = 0;
        }

        if (dim > COEFFICIENTS.length) {
            throw new Error("Out of range dimension");
            //var data = fs.readFileSync(file);
            //lines = ("" + data).split("\n");
        }
        else
            lines = COEFFICIENTS;

        for (i = 1; i <= BITS; i++) direction[0][i] = 1 << (BITS - i);
        for (var d = 1; d < dim; d++) {
            var cells = lines[d].split(/\s+/);
            var s = +cells[1];
            var a = +cells[2];
            var m = [0];
            for (i = 0; i < s; i++) m.push(+cells[3 + i]);
            for (i = 1; i <= s; i++) direction[d][i] = m[i] << (BITS - i);
            for (i = s + 1; i <= BITS; i++) {
                direction[d][i] = direction[d][i - s] ^ (direction[d][i - s] >> s);
                for (var k = 1; k <= s - 1; k++)
                direction[d][i] ^= ((a >> (s - 1 - k)) & 1) * direction[d][i - k];
            }
        }

        return sobol;
    };


    // same as d3.svg.arc... but for canvas
    d3.canvas.arc = function() {
        var innerRadius = d3_svg_arcInnerRadius,
        outerRadius = d3_svg_arcOuterRadius,
        cornerRadius = d3_zero,
        padRadius = d3_svg_arcAuto,
        startAngle = d3_svg_arcStartAngle,
        endAngle = d3_svg_arcEndAngle,
        padAngle = d3_svg_arcPadAngle,
        ctx;

        function arc () {
            var r0 = Math.max(0, +innerRadius.apply(arc, arguments)),
                r1 = Math.max(0, +outerRadius.apply(arc, arguments)),
                a0 = startAngle.apply(arc, arguments) - halfπ,
                a1 = endAngle.apply(arc, arguments) - halfπ,
                da = Math.abs(a1 - a0),
                cw = a0 > a1 ? 0 : 1;

            // Ensure that the outer radius is always larger than the inner radius.
            if (r1 < r0) rc = r1, r1 = r0, r0 = rc;

            ctx.beginPath();

            // Special case for an arc that spans the full circle.
            if (da >= τε) {
                ctx.arc(0, 0, r1, 0, τ, false);
                if (r0)
                    ctx.arc(0, 0, r0, 0, τ, true);
                ctx.closePath();
                return;
            }

            var rc,
                cr,
                rp,
                laf,
                l0,
                l1,
                ap = (+padAngle.apply(arc, arguments) || 0) / 2,
                p0 = 0,
                p1 = 0,
                x0 = null,
                y0 = null,
                x1 = null,
                y1 = null,
                x2 = null,
                y2 = null,
                x3 = null,
                y3 = null,
                path = [];

            // The recommended minimum inner radius when using padding is outerRadius *
            // padAngle / sin(θ), where θ is the angle of the smallest arc (without
            // padding). For example, if the outerRadius is 200 pixels and the padAngle
            // is 0.02 radians, a reasonable θ is 0.04 radians, and a reasonable
            // innerRadius is 100 pixels.

            if (ap) {
                rp = padRadius === d3_svg_arcAuto ? Math.sqrt(r0 * r0 + r1 * r1) : +padRadius.apply(arc, arguments);
                if (!cw) p1 *= -1;
                if (r1) p1 = d3_asin(rp / r1 * Math.sin(ap));
                if (r0) p0 = d3_asin(rp / r0 * Math.sin(ap));
            }

            // Compute the two outer corners.
            if (r1) {
                x0 = r1 * Math.cos(a0 + p1);
                y0 = r1 * Math.sin(a0 + p1);
                x1 = r1 * Math.cos(a1 - p1);
                y1 = r1 * Math.sin(a1 - p1);

                // Detect whether the outer corners are collapsed.
                l1 = Math.abs(a1 - a0 - 2 * p1) <= π ? 0 : 1;
                if (p1 && d3_svg_arcSweep(x0, y0, x1, y1) === cw ^ l1) {
                    var h1 = (a0 + a1) / 2;
                    x0 = r1 * Math.cos(h1);
                    y0 = r1 * Math.sin(h1);
                    x1 = y1 = null;
                }
            } else {
                x0 = y0 = 0;
            }

            // Compute the two inner corners.
            if (r0) {
                x2 = r0 * Math.cos(a1 - p0);
                y2 = r0 * Math.sin(a1 - p0);
                x3 = r0 * Math.cos(a0 + p0);
                y3 = r0 * Math.sin(a0 + p0);

                // Detect whether the inner corners are collapsed.
                l0 = Math.abs(a0 - a1 + 2 * p0) <= π ? 0 : 1;
                if (p0 && d3_svg_arcSweep(x2, y2, x3, y3) === (1 - cw) ^ l0) {
                    var h0 = (a0 + a1) / 2;
                    x2 = r0 * Math.cos(h0);
                    y2 = r0 * Math.sin(h0);
                    x3 = y3 = null;
                }
            } else
                x2 = y2 = 0;

            // Compute the rounded corners.
            if ((rc = Math.min(Math.abs(r1 - r0) / 2, +cornerRadius.apply(arc, arguments))) > 1e-3) {
                cr = r0 < r1 ^ cw ? 0 : 1;

                // Compute the angle of the sector formed by the two sides of the arc.
                var oc = x3 === null ? [x2, y2] : x1 === null ? [x0, y0] : d3_geom_polygonIntersect([x0, y0], [x3, y3], [x1, y1], [x2, y2]),
                    ax = x0 - oc[0],
                    ay = y0 - oc[1],
                    bx = x1 - oc[0],
                    by = y1 - oc[1],
                    kc = 1 / Math.sin(Math.acos((ax * bx + ay * by) / (Math.sqrt(ax * ax + ay * ay) * Math.sqrt(bx * bx + by * by))) / 2),
                    lc = Math.sqrt(oc[0] * oc[0] + oc[1] * oc[1]);

                // Compute the outer corners.
                if (x1 !== null) {
                    var rc1 = Math.min(rc, (r1 - lc) / (kc + 1)),
                        t30 = d3_svg_arcCornerTangents(x3 === null ? [x2, y2] : [x3, y3], [x0, y0], r1, rc1, cw),
                        t12 = d3_svg_arcCornerTangents([x1, y1], [x2, y2], r1, rc1, cw);

                    // Detect whether the outer edge is fully circular.
                    if (rc === rc1) {
                        laf = (1 - cw) ^ d3_svg_arcSweep(t30[1][0], t30[1][1], t12[1][0], t12[1][1]);
                        drawArc(ctx, t30[0], t30[1], rc1, 0, cr);
                        drawArc(ctx, t30[1], t12[1], r1, laf, cw);
                        drawArc(ctx, t12[1], t12[0], rc1, 0, cr);
                        //ctx.moveTo(t12[0][0], t12[0][1]);
                    } else {
                        drawArc(ctx, t30[0], t12[0], rc1, 1, cr);
                        //ctx.moveTo(t12[0][0], t12[0][1]);
                    }
                } else
                    ctx.moveTo(x0, y0);

                // Compute the inner corners.
                if (x3 !== null) {
                    var rc0 = Math.min(rc, (r0 - lc) / (kc - 1)),
                        t03 = d3_svg_arcCornerTangents([x0, y0], [x3, y3], r0, -rc0, cw),
                        t21 = d3_svg_arcCornerTangents([x2, y2], x1 === null ? [x0, y0] : [x1, y1], r0, -rc0, cw);

                    // Detect whether the inner edge is fully circular.
                    ctx.lineTo(t21[0][0], t21[0][1]);
                    if (rc === rc0) {
                        laf = cw ^ d3_svg_arcSweep(t21[1][0], t21[1][1], t03[1][0], t03[1][1]);
                        ctx.lineTo(t21[0][0], t21[0][1]);
                        drawArc(ctx, t21[0], t21[1], rc0, 0, cr);
                        drawArc(ctx, t21[1], t03[1], r0, laf, 1 - cw);
                        drawArc(ctx, t03[1], t03[0], rc0, 0, cr);
                    } else
                        drawArc(ctx, t21[0], t03[0], rc0, 0, cr);
                    //ctx.moveTo(t03[0][0], t03[0][1]);
                } else
                    ctx.lineTo(x2, y2);
            }

            // Compute straight corners.
            else {
                if (x1 !== null) {
                    drawArc(ctx, [x0, y0], [x1, y1], r1, l1, cw);
                }
                ctx.lineTo(x2, y2);
                if (x3 !== null) {
                    drawArc(ctx, [x2, y2], [x3, y3], r0, l0, 1 - cw);
                }
            }

            ctx.closePath();
        }

        arc.context = function (_) {
            if (!arguments.length) return ctx;
            ctx = _;
            return arc;
        };

        arc.innerRadius = function (v) {
            if (!arguments.length) return innerRadius;
            innerRadius = d3_functor(v);
            return arc;
        };

        arc.outerRadius = function (v) {
            if (!arguments.length) return outerRadius;
            outerRadius = d3_functor(v);
            return arc;
        };

        arc.cornerRadius = function (v) {
            if (!arguments.length) return cornerRadius;
            cornerRadius = d3_functor(v);
            return arc;
        };

        arc.padRadius = function (v) {
            if (!arguments.length) return padRadius;
            padRadius = v == d3_svg_arcAuto ? d3_svg_arcAuto : d3_functor(v);
            return arc;
        };

        arc.startAngle = function(v) {
            if (!arguments.length) return startAngle;
            startAngle = d3_functor(v);
            return arc;
        };

        arc.endAngle = function(v) {
            if (!arguments.length) return endAngle;
            endAngle = d3_functor(v);
            return arc;
        };

        arc.padAngle = function(v) {
            if (!arguments.length) return padAngle;
            padAngle = d3_functor(v);
            return arc;
        };

        arc.centroid = function() {
            var r = (+innerRadius.apply(arc, arguments) + outerRadius.apply(arc, arguments)) / 2,
                a = (+startAngle.apply(arc, arguments) + endAngle.apply(arc, arguments)) / 2 - halfπ;
            return [Math.cos(a) * r, Math.sin(a) * r];
        };

        return arc;
    };

    var drawArc = d3.canvas.drawArc = function (ctx, xyfrom, xyto, radius, laf, sweep) {
        var dx = xyfrom[0] - xyto[0],
            dy = xyfrom[1] - xyto[1],
            q2 = dx*dx + dy*dy,
            q = Math.sqrt(q2),
            xc = 0.5*(xyfrom[0] + xyto[0]),
            yc = 0.5*(xyfrom[1] + xyto[1]),
            l =  Math.sqrt(radius*radius - 0.25*q2);
        if (sweep > 0) {
            xc += l*dy/q;
            yc -= l*dx/q;
        } else {
            xc -= l*dy/q;
            yc += l*dx/q;
        }
        var a1 = Math.atan2(xyfrom[1]-yc, xyfrom[0]-xc),
            a2 = Math.atan2(xyto[1]-yc, xyto[0]-xc);
        ctx.arc(xc, yc, radius, a1, a2, sweep<=0);
    };



    // same as d3.svg.area... but for canvas
    d3.canvas.area = function() {
        return d3_canvas_area(d3_identity);
    };

    function d3_canvas_area(projection) {
        var x0 = d3_geom_pointX,
            x1 = d3_geom_pointX,
            y0 = 0,
            y1 = d3_geom_pointY,
            defined = d3_true,
            interpolate = d3_canvas_lineLinear,
            interpolateKey = interpolate.key,
            interpolateReverse = interpolate,
            tension = 0.7,
            ctx;

      function area(data) {
            if (!ctx) return;

            var segments = [],
                points0 = [],
                points1 = [],
                i = -1,
                n = data.length,
                d,
                fx0 = d3_functor(x0),
                fy0 = d3_functor(y0),
                fx1 = x0 === x1 ? function() { return x; } : d3_functor(x1),
                fy1 = y0 === y1 ? function() { return y; } : d3_functor(y1),
                x,
                y;

            function segment () {
                var p1 = projection(points1),
                    p0 = projection(points0.reverse());

                d3_canvas_move(ctx, p1[0], true);
                interpolate(ctx, p1, tension);
                d3_canvas_move(ctx, p0[0], interpolate.closed);
                interpolateReverse(ctx, p0, tension);
                ctx.closePath();
            }

            while (++i < n) {
                if (defined.call(area, d = data[i], i)) {
                    points0.push([x = +fx0.call(area, d, i), y = +fy0.call(area, d, i)]);
                    points1.push([+fx1.call(area, d, i), +fy1.call(area, d, i)]);
                } else if (points0.length) {
                    segment();
                    points0 = [];
                    points1 = [];
                }
            }

            if (points0.length) segment();

            return segments.length ? segments.join("") : null;
        }

        area.context = function (_) {
            if (!arguments.length) return ctx;
            ctx = _;
            return area;
        };

        area.x = function(_) {
            if (!arguments.length) return x1;
            x0 = x1 = _;
            return area;
        };

        area.x0 = function(_) {
            if (!arguments.length) return x0;
            x0 = _;
            return area;
        };

        area.x1 = function(_) {
            if (!arguments.length) return x1;
            x1 = _;
            return area;
        };

        area.y = function(_) {
            if (!arguments.length) return y1;
            y0 = y1 = _;
            return area;
        };

        area.y0 = function(_) {
            if (!arguments.length) return y0;
            y0 = _;
            return area;
        };

        area.y1 = function(_) {
            if (!arguments.length) return y1;
            y1 = _;
            return area;
        };

        area.defined  = function(_) {
            if (!arguments.length) return defined;
            defined = _;
            return area;
        };

        area.interpolate = function(_) {
            if (!arguments.length) return interpolateKey;
            if (typeof _ === "function") interpolateKey = interpolate = _;
            else interpolateKey = (interpolate = d3_canvas_lineInterpolators.get(_) || d3_canvas_lineLinear).key;
            interpolateReverse = interpolate.reverse || interpolate;
            return area;
        };

        area.tension = function(_) {
            if (!arguments.length) return tension;
            tension = _;
            return area;
        };

        return area;
    }


    // same as d3.svg.axis... but for canvas
    d3.canvas.axis = function() {
        var scale = d3.scale.linear(),
            orient = d3_canvas_axisDefaultOrient,
            innerTickSize = 6,
            outerTickSize = 6,
            tickPadding = 3,
            tickArguments_ = [10],
            tickValues = null,
            tickFormat_ = null,
            textRotate = 0,
            textAlign = null;

        function axis (canvas) {
            canvas.each(function() {
                var ctx = this.getContext('2d'),
                    scale0 = this.__chart__ || scale,
                    scale1 = this.__chart__ = scale.copy();

                // Ticks, or domain values for ordinal scales.
                var ticks = tickValues === null ? (scale1.ticks ? scale1.ticks.apply(scale1, tickArguments_) : scale1.domain()) : tickValues,
                    tickFormat = tickFormat_ === null ? (scale1.tickFormat ? scale1.tickFormat.apply(scale1, tickArguments_) : d3_identity) : tickFormat_,
                    tickSpacing = Math.max(innerTickSize, 0) + tickPadding,
                    sign = orient === "top" || orient === "left" ? -1 : 1,
                    tickTransform,
                    trange;

                // Domain.
                var range = d3_scaleRange(scale1);

                if (scale1.rangeBand) {
                    var x = scale1, dx = x.rangeBand()/2;
                    scale0 = scale1 = function (d) { return x(d) + dx; };
                } else if (scale0.rangeBand) {
                    scale0 = scale1;
                }

                // Apply axis labels on major ticks
                if (orient === "bottom" || orient === "top") {
                    ctx.textBaseline = sign < 0 ? 'bottom' : 'top';
                    ctx.textAlign = textAlign || 'center';
                    ctx.moveTo(range[0], 0);
                    ctx.lineTo(range[1], 0);
                    ctx.moveTo(range[0], 0);
                    ctx.lineTo(range[0], sign*outerTickSize);
                    ctx.moveTo(range[1], 0);
                    ctx.lineTo(range[1], sign*outerTickSize);
                    ticks.forEach(function (tick, index) {
                        trange = scale1(tick);
                        ctx.moveTo(trange, 0);
                        ctx.lineTo(trange, sign*innerTickSize);
                        if (textRotate) {
                            ctx.save();
                            ctx.translate(trange, sign*tickSpacing);
                            ctx.rotate(textRotate);
                            ctx.fillText(tickFormat(tick), 0, 0);
                            ctx.restore();
                        } else
                            ctx.fillText(tickFormat(tick), trange, sign*tickSpacing);
                    });
                } else {
                    ctx.textBaseline = 'middle';
                    ctx.textAlign = textAlign || (sign < 0 ? "end" : "start");
                    ctx.moveTo(0, range[0]);
                    ctx.lineTo(0, range[1]);
                    ctx.moveTo(0, range[0]);
                    ctx.lineTo(sign*outerTickSize, range[0]);
                    ctx.moveTo(0, range[1]);
                    ctx.lineTo(sign*outerTickSize, range[1]);
                    ticks.forEach(function (tick, index) {
                        trange = scale1(tick);
                        ctx.moveTo(0, trange);
                        ctx.lineTo(sign*innerTickSize, trange);
                        if (textRotate) {
                            ctx.save();
                            ctx.rotate(textRotate);
                            ctx.fillText(tickFormat(tick), sign*tickSpacing, trange);
                            ctx.restore();
                        } else
                            ctx.fillText(tickFormat(tick), sign*tickSpacing, trange);
                    });
                }
            });
        }

        axis.scale = function(x) {
            if (!arguments.length) return scale;
            scale = x;
            return axis;
        };

        axis.orient = function(x) {
            if (!arguments.length) return orient;
            orient = x in d3_canvas_axisOrients ? x + "" : d3_canvas_axisDefaultOrient;
            return axis;
        };

        axis.ticks = function() {
            if (!arguments.length) return tickArguments_;
            tickArguments_ = arguments;
            return axis;
        };

        axis.tickValues = function(x) {
            if (!arguments.length) return tickValues;
            tickValues = x;
            return axis;
        };

        axis.tickFormat = function(x) {
            if (!arguments.length) return tickFormat_;
            tickFormat_ = x;
            return axis;
        };

        axis.tickSize = function(x) {
            var n = arguments.length;
            if (!n) return innerTickSize;
            innerTickSize = +x;
            outerTickSize = +arguments[n - 1];
            return axis;
        };

        axis.innerTickSize = function(x) {
            if (!arguments.length) return innerTickSize;
            innerTickSize = +x;
            return axis;
        };

        axis.outerTickSize = function(x) {
            if (!arguments.length) return outerTickSize;
            outerTickSize = +x;
            return axis;
        };

        axis.tickPadding = function(x) {
            if (!arguments.length) return tickPadding;
            tickPadding = +x;
            return axis;
        };

        axis.tickSubdivide = function() {
            return arguments.length && axis;
        };

        axis.textRotate = function (x) {
            if (!arguments.length) return textRotate;
            textRotate = +x;
            return axis;
        };

        axis.textAlign = function (x) {
            if (!arguments.length) return textAlign;
            textAlign = x;
            return axis;
        };

        return axis;
    };

    var d3_canvas_axisDefaultOrient = "bottom",
        d3_canvas_axisOrients = {top: 1, right: 1, bottom: 1, left: 1};



    d3.canvas.brush = function() {
        var event = d3.dispatch("brushstart", "brush", "brushend"),
            x = null, // x-scale, optional
            y = null, // y-scale, optional
            xExtent = [0, 0], // [x0, x1] in integer pixels
            yExtent = [0, 0], // [y0, y1] in integer pixels
            xExtentDomain, // x-extent in data space
            yExtentDomain, // y-extent in data space
            xClamp = true, // whether to clamp the x-extent to the range
            yClamp = true, // whether to clamp the y-extent to the range
            resizes = d3_svg_brushResizes[0],
            rect = [0, 0, 0, 0], // specify a rectangle in the canvas where to limit the extent
            factor = window.devicePixelRatio || 1,
            p = 3*factor,
            fillStyle,
            draw_sn,
            draw_we;

        function brush(canvas) {

            canvas.each(function () {
                d3.select(this)
                    .style("pointer-events", "all")
                    .style("-webkit-tap-highlight-color", "rgba(0,0,0,0)")
                    .on("mousedown.brush", Brushstart)
                    .on("touchstart.brush", Brushstart)
                    .on("mousemove.brushover", Brushover);
                event.brushstart.call(this);
                event.brush.call(this);
                event.brushend.call(this);
                brushfill(this.getContext('2d'));
            });
        }

        function brushfill (ctx) {
            if (fillStyle) {
                draw(ctx);
                ctx.fillStyle = fillStyle;
                ctx.fill();
            }
        }

        function draw (ctx) {
            var x0, y0;

            ctx.beginPath();

            if (x & y) {
                x0 = x(extent[0][0]);
                y0 = y(extent[1][0]);
            }
            else if (x) {
                x0 = xExtent[0];
                ctx.rect(x0 + rect[0], rect[1], xExtent[1]-x0, rect[3] || ctx.canvas.height);
            }
            else if (y)
                ctx.rect(0, extent[0][0], ctx.canvas.width, extent[0][1]-extent[0][0]);
        }

        function draw_sn_ (ctx, sn) {
        }

        function draw_we_ (ctx, ew) {
            var xv = xExtent[ew];
            ctx.beginPath();
            ctx.rect(xv - p + rect[0], rect[1], 2*p, rect[3] || ctx.canvas.height);
        }

        function Brushover () {
            var canvas = d3.select(this),
                ctx = this.getContext('2d'),
                origin = d3.canvas.mouse(this),
                xp = origin[0],
                yp = origin[1],
                resize = '';

            if (y) {
                draw_sn(ctx, 0);
                if (ctx.isPointInPath(xp, yp)) resize = 's';
                else {
                    draw_sn(ctx, 1);
                    if (ctx.isPointInPath(xp, yp)) resize = 'n';
                }
            }
            if (x) {
                draw_we(ctx, 0);
                if (ctx.isPointInPath(xp, yp)) resize += 'w';
                else {
                    draw_we_(ctx, 1);
                    if (ctx.isPointInPath(xp, yp)) resize += 'e';
                }
            }
            draw(ctx);
            if (resize) {
                canvas.style('cursor', d3_svg_brushCursor[resize])
                    .datum(resize).classed('extent', false);
            } else {
                if (ctx.isPointInPath(xp, yp))
                    canvas.style('cursor', 'move').classed('extent', true).datum('');
                else
                    canvas.style('cursor', 'crosshair').classed('extent', false).datum('');
            }
        }

        function Brushstart() {
            var target = this,
                ctx = target.getContext('2d'),
                origin = d3.canvas.mouse(target),
                //event_ = event.of(target, arguments),
                canvas = d3.select(target),
                resizing = canvas.datum(),
                resizingX = !/^(n|s)$/.test(resizing) && x,
                resizingY = !/^(e|w)$/.test(resizing) && y,
                dragging = canvas.classed("extent"),
                center,
                offset;

            var w = d3.select(window)
                .on("keydown.brush", keydown)
                .on("keyup.brush", keyup);

            if (d3.event.changedTouches) {
                w.on("touchmove.brush", brushmove).on("touchend.brush", brushend);
            } else {
                w.on("mousemove.brush", brushmove).on("mouseup.brush", brushend);
            }

            // Interrupt the transition, if any.
            canvas.interrupt().selectAll("*").interrupt();

            // If the extent was clicked on, drag rather than brush;
            // store the point between the mouse and extent origin instead.
            if (dragging) {
                origin[0] = xExtent[0] - origin[0];
                origin[1] = yExtent[0] - origin[1];
            }

            // If a resizer was clicked on, record which side is to be resized.
            // Also, set the origin to the opposite side.
            else if (resizing) {
                var ex = +/w$/.test(resizing),
                ey = +/^n/.test(resizing);
                offset = [xExtent[1 - ex] - origin[0], yExtent[1 - ey] - origin[1]];
                origin[0] = xExtent[ex];
                origin[1] = yExtent[ey];
            }

            // If the ALT key is down when starting a brush, the center is at the mouse.
            else if (d3.event.altKey) center = origin.slice();

            // Propagate the active cursor to the body for the drag duration.
            d3.select("body").style("cursor", canvas.style("cursor"));

            // Notify listeners.
            event.brushstart({type: "brushstart"});

            brushmove();

            function keydown() {
                if (d3.event.keyCode == 32) {
                    if (!dragging) {
                        center = null;
                        origin[0] -= xExtent[1];
                        origin[1] -= yExtent[1];
                        dragging = 2;
                    }
                    d3.event.preventDefault();
                }
            }

            function keyup() {
                if (d3.event.keyCode == 32 && dragging == 2) {
                    origin[0] += xExtent[1];
                    origin[1] += yExtent[1];
                    dragging = 0;
                    d3.event.preventDefault();
                }
            }

            function brushmove() {
                var point = d3.canvas.mouse(target);

                d3.canvas.clear(ctx);

                // Preserve the offset for thick resizers.
                if (offset) {
                    point[0] += offset[0];
                    point[1] += offset[1];
                }

                if (!dragging) {

                    // If needed, determine the center from the current extent.
                    if (d3.event.altKey) {
                        if (!center) center = [(xExtent[0] + xExtent[1]) / 2, (yExtent[0] + yExtent[1]) / 2];

                        // Update the origin, for when the ALT key is released.
                        origin[0] = xExtent[+(point[0] < center[0])];
                        origin[1] = yExtent[+(point[1] < center[1])];
                    }

                    // When the ALT key is released, we clear the center.
                    else center = null;
                }

                var ev = {type: "brush"};

                // Final redraw and notify listeners.
                if ((resizingX && move1(point, x, 0)) ||
                    (resizingY && move1(point, y, 1)))
                    ev.mode = dragging ? "move" : "resize";

                event.brush.call(ctx, {type: "brush", mode: dragging ? "move" : "resize"});
                brushfill(ctx);
            }

            function move1(point, scale, i) {
                var range = d3_scaleRange(scale),
                    r0 = range[0],
                    r1 = range[1],
                    position = origin[i],
                    extent = i ? yExtent : xExtent,
                    size = extent[1] - extent[0],
                    min,
                    max;

                // When dragging, reduce the range by the extent size and position.
                if (dragging) {
                    r0 -= position;
                    r1 -= size + position;
                }

                // Clamp the point (unless clamp set to false) so that the extent fits within the range extent.
                min = (i ? yClamp : xClamp) ? Math.max(r0, Math.min(r1, point[i])) : point[i];

                // Compute the new extent bounds.
                if (dragging) {
                    max = (min += position) + size;
                } else {

                    // If the ALT key is pressed, then preserve the center of the extent.
                    if (center) position = Math.max(r0, Math.min(r1, 2 * center[i] - min));

                    // Compute the min and max of the position and point.
                    if (position < min) {
                        max = min;
                        min = position;
                    } else {
                        max = position;
                    }
                }

                // Update the stored bounds.
                if (extent[0] != min || extent[1] != max) {
                    if (i) yExtentDomain = null;
                    else xExtentDomain = null;
                    extent[0] = min;
                    extent[1] = max;
                    return true;
                }
            }

            function brushend() {
                brushmove();

                // reset the cursor styles
                d3.select("body").style("cursor", null);

                w.on("mousemove.brush", null)
                    .on("mouseup.brush", null)
                    .on("touchmove.brush", null)
                    .on("touchend.brush", null)
                    .on("keydown.brush", null)
                    .on("keyup.brush", null);

                event.brushend.call(ctx, {type: "brushend"});
            }
        }

        brush.draw_sn = function (_) {
            if (!arguments.length) return draw_sn;
            draw_sn = d3_functor(_);
            return brush;
        };

        brush.draw_we = function (_) {
            if (!arguments.length) return draw_we;
            draw_we = d3_functor(_);
            return brush;
        };

        brush.fillStyle = function (_) {
            if (!arguments.length) return fillStyle;
            fillStyle = _;
            return brush;
        };

        brush.rect = function (_) {
            if (!arguments.length) return rect;
            rect = _;
            return brush;
        };

        brush.x = function(z) {
            if (!arguments.length) return x;
            x = z;
            resizes = d3_svg_brushResizes[!x << 1 | !y]; // fore!
            return brush;
        };

        brush.y = function(z) {
            if (!arguments.length) return y;
            y = z;
            resizes = d3_svg_brushResizes[!x << 1 | !y]; // fore!
            return brush;
        };

        brush.clamp = function(z) {
            if (!arguments.length) return x && y ? [xClamp, yClamp] : x ? xClamp : y ? yClamp : null;
            if (x && y) xClamp = !!z[0], yClamp = !!z[1];
            else if (x) xClamp = !!z;
            else if (y) yClamp = !!z;
            return brush;
        };

        brush.extent = function(z) {
            var x0, x1, y0, y1, t;

            // Invert the pixel extent to data-space.
            if (!arguments.length) {
              if (x) {
                if (xExtentDomain) {
                  x0 = xExtentDomain[0], x1 = xExtentDomain[1];
                } else {
                  x0 = xExtent[0], x1 = xExtent[1];
                  if (x.invert) x0 = x.invert(x0), x1 = x.invert(x1);
                  if (x1 < x0) t = x0, x0 = x1, x1 = t;
                }
              }
              if (y) {
                if (yExtentDomain) {
                  y0 = yExtentDomain[0], y1 = yExtentDomain[1];
                } else {
                  y0 = yExtent[0], y1 = yExtent[1];
                  if (y.invert) y0 = y.invert(y0), y1 = y.invert(y1);
                  if (y1 < y0) t = y0, y0 = y1, y1 = t;
                }
              }
              return x && y ? [[x0, y0], [x1, y1]] : x ? [x0, x1] : y && [y0, y1];
            }

            // Scale the data-space extent to pixels.
            if (x) {
              x0 = z[0], x1 = z[1];
              if (y) x0 = x0[0], x1 = x1[0];
              xExtentDomain = [x0, x1];
              if (x.invert) x0 = x(x0), x1 = x(x1);
              if (x1 < x0) t = x0, x0 = x1, x1 = t;
              if (x0 != xExtent[0] || x1 != xExtent[1]) xExtent = [x0, x1]; // copy-on-write
            }
            if (y) {
              y0 = z[0], y1 = z[1];
              if (x) y0 = y0[1], y1 = y1[1];
              yExtentDomain = [y0, y1];
              if (y.invert) y0 = y(y0), y1 = y(y1);
              if (y1 < y0) t = y0, y0 = y1, y1 = t;
              if (y0 != yExtent[0] || y1 != yExtent[1]) yExtent = [y0, y1]; // copy-on-write
            }

            return brush;
          };

        brush.clear = function() {
            if (!brush.empty()) {
              xExtent = [0, 0], yExtent = [0, 0]; // copy-on-write
              xExtentDomain = yExtentDomain = null;
            }
            return brush;
        };

        brush.empty = function() {
            return !!x && xExtent[0] == xExtent[1] || !!y && yExtent[0] == yExtent[1];
        };

        brush.draw_sn(draw_sn_).draw_we(draw_we_);

        return d3.rebind(brush, event, "on");

    };


    d3.canvas.pixelRatio = window.devicePixelRatio || 1;

    d3.canvas.webgl = function (canvas) {
        if (!arguments.length) canvas = document.createElement('canvas');
        try {
            return canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        } catch (e) {
            return;
        }
    };

    d3.canvas.clear = function (ctx) {
        ctx.beginPath();
        ctx.closePath();
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0 , 0, ctx.canvas.width, ctx.canvas.height);
    };


    d3.canvas.retinaScale = function(ctx, width, height){
        ctx.canvas.width = width;
        ctx.canvas.height = height;

        if (window.devicePixelRatio) {
            ctx.canvas.style.width = width + "px";
            ctx.canvas.style.height = height + "px";
            ctx.canvas.width = width * window.devicePixelRatio;
            ctx.canvas.height = height * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        }

        d3.canvas.clear(ctx);
        return d3.canvas.pixelRatio;
    };


    d3.canvas.resize = function (ctx, width, height) {
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect (0 , 0, ctx.canvas.width, ctx.canvas.height);
        return d3.canvas.retinaScale(ctx, width, height);
    };

    d3.canvas.style = function (ctx, d) {
        if (d.fill) {
            ctx.fillStyle = d3.canvas.rgba(d.fill, d.fillOpacity);
            ctx.fill();
        }
        if (d.color && d.lineWidth) {
            ctx.strokeStyle = d3.canvas.rgba(d.color, d.colorOpacity);
            ctx.lineWidth = d3.canvas.pixelRatio*d.lineWidth;
            ctx.stroke();
        }
    };

    d3.canvas.drawPolygon = function (ctx, pts, radius) {
        if (radius > 0)
            pts = getRoundedPoints(pts, radius);
        var i, pt, len = pts.length;
        ctx.beginPath();
        for (i = 0; i < len; i++) {
            pt = pts[i];
            if (i === 0)
                ctx.moveTo(pt[0], pt[1]);
            else
                ctx.lineTo(pt[0], pt[1]);
            if (radius > 0)
                ctx.quadraticCurveTo(pt[2], pt[3], pt[4], pt[5]);
        }
        ctx.closePath();
    };

    d3.canvas.rgba = function (color, opacity) {
        if (opacity < 1) {
            var c = d3.rgb(color);
            return 'rgba(' + c.r + ',' + c.g + ',' + c.b + ',' + opacity + ')';
        } else
            return color;
    };

    d3.canvas.mouse = function (container) {
        var point = d3.mouse(container);
        if (container.getContext && window.devicePixelRatio) {
            point[0] *= window.devicePixelRatio;
            point[1] *= window.devicePixelRatio;
        }
        return point;
    };

    function getRoundedPoints(pts, radius) {
        var i1, i2, i3, p1, p2, p3, prevPt, nextPt,
            len = pts.length,
            res = new Array(len);
        for (i2 = 0; i2 < len; i2++) {
            i1 = i2-1;
            i3 = i2+1;
            if (i1 < 0)
                i1 = len - 1;
            if (i3 === len) i3 = 0;
            p1 = pts[i1];
            p2 = pts[i2];
            p3 = pts[i3];
            prevPt = getRoundedPoint(p1[0], p1[1], p2[0], p2[1], radius, false);
            nextPt = getRoundedPoint(p2[0], p2[1], p3[0], p3[1], radius, true);
            res[i2] = [prevPt[0], prevPt[1], p2[0], p2[1], nextPt[0], nextPt[1]];
        }
      return res;
    }

    function getRoundedPoint(x1, y1, x2, y2, radius, first) {
        var total = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2)),
            idx = first ? radius / total : (total - radius) / total;
        return [x1 + (idx * (x2 - x1)), y1 + (idx * (y2 - y1))];
    }


    // same as d3.svg.line... but for canvas
    d3.canvas.line = function() {
        return d3_canvas_line(d3_identity);
    };


    function d3_canvas_line (projection) {
        var x = d3_geom_pointX,
            y = d3_geom_pointY,
            defined = d3_true,
            interpolate = d3_canvas_lineLinear,
            interpolateKey = interpolate.key,
            tension = 0.7,
            ctx;

        function line (data) {
            if (!ctx) return;

            var segments = [],
                points = [],
                i = -1,
                n = data.length,
                d,
                fx = d3_functor(x),
                fy = d3_functor(y);

            function segment () {
                var p = projection(points);
                d3_canvas_move(ctx, p[0], true);
                interpolate(ctx, p, tension);
            }

            while (++i < n) {
                if (defined.call(line, d = data[i], i)) {
                    points.push([+fx.call(line, d, i), +fy.call(line, d, i)]);
                } else if (points.length) {
                    segment();
                    points = [];
                }
            }

            if (points.length) segment();

            return segments.length ? segments.join("") : null;
        }

        line.context = function (_) {
            if (!arguments.length) return ctx;
            ctx = _;
            return line;
        };

        line.x = function(_) {
            if (!arguments.length) return x;
            x = _;
            return line;
        };

        line.y = function(_) {
            if (!arguments.length) return y;
            y = _;
            return line;
        };

        line.defined  = function(_) {
            if (!arguments.length) return defined;
            defined = _;
            return line;
        };

        line.interpolate = function(_) {
            if (!arguments.length) return interpolateKey;
            if (typeof _ === "function") interpolateKey = interpolate = _;
            else interpolateKey = (interpolate = d3_canvas_lineInterpolators.get(_) || d3_canvas_lineLinear).key;
            return line;
        };

        line.tension = function(_) {
            if (!arguments.length) return tension;
            tension = _;
            return line;
        };

        return line;
    }


    var d3_canvas_lineInterpolators = d3.map({
        "linear": d3_canvas_lineLinear,
        "linear-closed": d3_canvas_lineLinearClosed,
        "step": d3_canvas_lineStep,
        "step-before": d3_canvas_lineStepBefore,
        "step-after": d3_canvas_lineStepAfter,
        "basis": d3_canvas_lineBasis,
        "basis-open": d3_canvas_lineBasisOpen,
        "basis-closed": d3_canvas_lineBasisClosed,
        "bundle": d3_canvas_lineBundle,
        "cardinal": d3_canvas_lineCardinal,
        "cardinal-open": d3_canvas_lineCardinalOpen,
        "cardinal-closed": d3_canvas_lineCardinalClosed,
        "monotone": d3_canvas_lineMonotone
    });

    function d3_canvas_move(ctx, point, move) {
        if (move) {
            ctx.beginPath();
            ctx.moveTo(point[0], point[1]);
        } else {
            ctx.lineTo(point[0], point[1]);
        }
    }

    function d3_canvas_lineLinear(ctx, points) {
        var p = points[0];
        for (var i=1; i<points.length; ++i) {
            p = points[i];
            ctx.lineTo(p[0], p[1]);
        }
    }

    function d3_canvas_lineLinearClosed(ctx, points) {
        d3_canvas_lineLinear(ctx, points);
        ctx.closePath();
    }

    function d3_canvas_lineStep(ctx, points) {
        var pn = points[1], p = points[0],
            x = 0.5*(pn[0] + p[0]);
        ctx.lineTo(x, p[1]);
        ctx.lineTo(x, pn[1]);
        for (var i=2; i<points.length; ++i) {
            p = pn;
            pn = points[i];
            x = 0.5*(pn[0] + p[0]);
            ctx.lineTo(x, p[1]);
            ctx.lineTo(x, pn[1]);
        }
        ctx.lineTo(pn[0], pn[1]);
    }

    function d3_canvas_lineStepBefore(ctx, points) {
        var pn = points[0], p;
        for (var i=1; i<points.length; ++i) {
            p = pn;
            pn = points[i];
            ctx.lineTo(p[0], pn[1]);
            ctx.lineTo(pn[0], pn[1]);
        }
    }

    function d3_canvas_lineStepAfter(ctx, points) {
        var pn = points[0], p;
        for (var i=1; i<points.length; ++i) {
            p = pn;
            pn = points[i];
            ctx.lineTo(pn[0], p[1]);
            ctx.lineTo(pn[0], pn[1]);
        }
    }

    function d3_canvas_lineBasis(ctx, points) {
        if (points.length < 3) return d3_canvas_lineLinear(ctx, points);
        var i = 1,
            n = points.length,
            pi = points[0],
            x0 = pi[0],
            y0 = pi[1],
            px = [x0, x0, x0, (pi = points[1])[0]],
            py = [y0, y0, y0, pi[1]];

        ctx.lineTo(d3_svg_lineDot4(d3_svg_lineBasisBezier3, px),
                   d3_svg_lineDot4(d3_svg_lineBasisBezier3, py));

        points.push(points[n - 1]);
        while (++i <= n) {
            pi = points[i];
            px.shift();
            px.push(pi[0]);
            py.shift();
            py.push(pi[1]);
            d3_canvas_lineBasisBezier(ctx, px, py);
        }
        points.pop();
        ctx.lineTo(pi[0], pi[1]);
    }

    // Open B-spline interpolation; generates "C" commands.
    function d3_canvas_lineBasisOpen(ctx, points) {
        if (points.length < 4) return d3_canvas_lineLinear(points);
        var path = [],
            i = -1,
            n = points.length,
            pi,
            px = [0],
            py = [0];
        while (++i < 3) {
            pi = points[i];
            px.push(pi[0]);
            py.push(pi[1]);
        }
        ctx.moveTo(d3_svg_lineDot4(d3_svg_lineBasisBezier3, px),
                   d3_svg_lineDot4(d3_svg_lineBasisBezier3, py));
        --i; while (++i < n) {
            pi = points[i];
            px.shift(); px.push(pi[0]);
            py.shift(); py.push(pi[1]);
            d3_canvas_lineBasisBezier(ctx, px, py);
        }
    }

    // Closed B-spline interpolation; generates "C" commands.
    function d3_canvas_lineBasisClosed(ctx, points) {
        var path,
            i = -1,
            n = points.length,
            m = n + 4,
            pi,
            px = [],
            py = [];
        while (++i < 4) {
            pi = points[i % n];
            px.push(pi[0]);
            py.push(pi[1]);
        }
        ctx.moveTo(d3_svg_lineDot4(d3_svg_lineBasisBezier3, px),
                   d3_svg_lineDot4(d3_svg_lineBasisBezier3, py));
        --i; while (++i < m) {
            pi = points[i % n];
            px.shift(); px.push(pi[0]);
            py.shift(); py.push(pi[1]);
            d3_canvas_lineBasisBezier(ctx, px, py);
        }
    }

    function d3_canvas_lineBundle(ctx, points, tension) {
        var n = points.length - 1;
        if (n) {
            var x0 = points[0][0],
                y0 = points[0][1],
                dx = points[n][0] - x0,
                dy = points[n][1] - y0,
                i = -1,
                p,
                t;
            while (++i <= n) {
                p = points[i];
                t = i / n;
                p[0] = tension * p[0] + (1 - tension) * (x0 + t * dx);
                p[1] = tension * p[1] + (1 - tension) * (y0 + t * dy);
            }
        }
        return d3_canvas_lineBasis(ctx, points);
    }

    function d3_canvas_lineCardinal(ctx, points, tension) {
        if (points.length < 3)
            d3_canvas_lineLinear(ctx, points);
        else {
            d3_canvas_lineHermite(ctx, points, d3_svg_lineCardinalTangents(points, tension));
        }
    }

    // Open cardinal spline interpolation; generates "C" commands.
    function d3_canvas_lineCardinalOpen(ctx, points, tension) {
        if (points.length < 4)
            d3_canvas_lineLinear(ctx, points);
        else {
            d3_canvas_lineHermite(ctx, points.slice(1, -1), d3_svg_lineCardinalTangents(points, tension));
        }
    }

    // Closed cardinal spline interpolation; generates "C" commands.
    function d3_canvas_lineCardinalClosed(ctx, points, tension) {
        if (points.length < 3)
            d3_canvas_lineLinear(ctx, points);
        else {
            d3_canvas_lineHermite(ctx, (points.push(points[0]), points),
                d3_svg_lineCardinalTangents([points[points.length - 2]].concat(points, [points[1]]), tension));
        }
    }

    function d3_canvas_lineMonotone(ctx, points) {
        if (points.length < 3)
            d3_canvas_lineLinear(ctx, points);
        else {
            d3_canvas_lineHermite(ctx, points, d3_svg_lineMonotoneTangents(points));
        }
    }


    function d3_canvas_lineBasisBezier(ctx, x, y) {
        ctx.bezierCurveTo(d3_svg_lineDot4(d3_svg_lineBasisBezier1, x),
                          d3_svg_lineDot4(d3_svg_lineBasisBezier1, y),
                          d3_svg_lineDot4(d3_svg_lineBasisBezier2, x),
                          d3_svg_lineDot4(d3_svg_lineBasisBezier2, y),
                          d3_svg_lineDot4(d3_svg_lineBasisBezier3, x),
                          d3_svg_lineDot4(d3_svg_lineBasisBezier3, y));
    }


    function d3_canvas_lineHermite(ctx, points, tangents) {
        if (tangents.length < 1 ||
            (points.length != tangents.length && points.length != tangents.length + 2))
            return d3_canvas_lineLinear(ctx, points);

        var quad = points.length != tangents.length,
            p0 = points[0],
            p = points[1],
            t0 = tangents[0],
            t = t0,
            pi = 1,
            xc, yc;

        if (quad) {
            ctx.quadraticCurveTo((p[0] - t0[0] * 2 / 3), (p[1] - t0[1] * 2 / 3), p[0], p[1]);
            p0 = points[1];
            pi = 2;
        }

        if (tangents.length > 1) {
            t = tangents[1];
            p = points[pi];
            pi++;
            ctx.bezierCurveTo(p0[0] + t0[0], p0[1] + t0[1],
                              p[0] - t[0], p[1] - t[1],
                              p[0], p[1]);
            for (var i = 2; i < tangents.length; i++, pi++) {
                xc = p[0] + t[0];
                yc = p[1] + t[1];
                p = points[pi];
                t = tangents[i];
                ctx.bezierCurveTo(xc, yc,
                                  p[0] - t[0], p[1] - t[1],
                                  p[0], p[1]);
            }
        }

        if (quad) {
            var lp = points[pi];
            ctx.quadraticCurveTo((p[0] + t[0] * 2 / 3), (p[1] + t[1] * 2 / 3), lp[0], lp[1]);
        }
    }

    d3_canvas_lineStepBefore.reverse = d3_canvas_lineStepAfter;
    d3_canvas_lineStepAfter.reverse = d3_canvas_lineStepBefore;


    // same as d3.svg.symbol... but for canvas
    d3.canvas.symbol = function() {
        var svg = d3.svg.symbol(),
            type = svg.type(),
            size = svg.size(),
            ctx;

        function symbol (d, i) {
            return (d3_canvas_symbols.get(type.call(symbol, d, i)) || d3_canvas_symbolCircle)(ctx, size.call(symbol, d, i));
        }

        symbol.type = function (x) {
            if (!arguments.length) return type;
            type = d3_functor(x);
            return symbol;
        };

        // size of symbol in square pixels
        symbol.size = function (x) {
            if (!arguments.length) return size;
            size = d3_functor(x);
            return symbol;
        };

        symbol.context = function (_) {
            if (!arguments.length) return ctx;
            ctx = _;
            return symbol;
        };

        return symbol;
    };


    function d3_canvas_symbolCircle(ctx, size) {
        var r = Math.sqrt(size / π);
        ctx.beginPath();
        ctx.arc(0, 0, r, 0, τ, false);
        ctx.closePath();
    }

    var d3_canvas_symbols = d3.map({
        "circle": d3_canvas_symbolCircle,
        "cross": function(ctx, size) {
            var r = Math.sqrt(size / 5) / 2,
                r3 = 3*r;
            ctx.beginPath();
            ctx.moveTo(-r3, -r);
            ctx.lineTo(-r, -r);
            ctx.lineTo(-r, -r3);
            ctx.lineTo(r, -r3);
            ctx.lineTo(r, -r);
            ctx.lineTo(r3, -r);
            ctx.lineTo(r3, r);
            ctx.lineTo(r, r);
            ctx.lineTo(r, r3);
            ctx.lineTo(-r, r3);
            ctx.lineTo(-r, r);
            ctx.lineTo(-r3, r);
            ctx.closePath();
        },
        "diamond": function(ctx, size) {
            var ry = Math.sqrt(size / (2 * d3_svg_symbolTan30)),
                rx = ry * d3_svg_symbolTan30;
            ctx.beginPath();
            ctx.moveTo(0, -ry);
            ctx.lineTo(rx, 0);
            ctx.lineTo(0, ry);
            ctx.lineTo(-rx, 0);
            ctx.closePath();
        },
        "square": function(ctx, size) {
            var s = Math.sqrt(size);
            ctx.beginPath();
            ctx.rect(-0.5*s, -0.5*s, s, s);
            ctx.closePath();
        },
        "triangle-down": function(ctx, size) {
            var rx = Math.sqrt(size / d3_svg_symbolSqrt3),
                ry = rx * d3_svg_symbolSqrt3 / 2;
            ctx.beginPath();
            ctx.moveTo(0, ry);
            ctx.lineTo(rx, -ry);
            ctx.lineTo(-rx, -ry);
            ctx.closePath();
        },
        "triangle-up": function(ctx, size) {
            var rx = Math.sqrt(size / d3_svg_symbolSqrt3),
                ry = rx * d3_svg_symbolSqrt3 / 2;
            ctx.beginPath();
            ctx.moveTo(0, -ry);
            ctx.lineTo(rx, ry);
            ctx.lineTo(-rx, ry);
            ctx.closePath();
        }
    });

    d3.canvas.symbolTypes = d3_canvas_symbols.keys();


    var d3_svg_symbolSqrt3 = Math.sqrt(3),
        d3_svg_symbolTan30 = Math.tan(30 * d3_radians);


    d3.canvas.transition = function(selection, name) {
        var transition = d3.transition(selection, name);

        return transition;
    };
    //
    //  Manage active elements in a paper
    function activeEvents (paper) {

        var activeElements = [],
            activeIn = [],
            activeOut = [],
            canvases = [],
            opts = paper.options(),
            index;

        paper.activeOut = function (d) {
            if (!arguments.length) {
                activeElements.forEach(function (a) {
                    paper.activeOut(a);
                });
            } else {
                if (activeOut.indexOf(d) === -1) activeOut.push(d);
                var index = activeIn.indexOf(d);
                if (index > -1) activeIn.splice(index, 1);
            }
            return paper;
        };

        //  Add an active element
        paper.activeIn = function (d) {
            if (activeIn.indexOf(d) === -1) activeIn.push(d);
            var index = activeOut.indexOf(d);
            if (index > -1) activeOut.splice(index, 1);
            return paper;
        };

        // paper task for
        //  * De-activating elements no longer active
        //  * Activating active elements
        paper.task(function () {
            var el;

            // clear canvases managing active events
            canvases.splice(0).forEach(function (ctx) {
                d3.canvas.clear(ctx);
            });

            if (activeOut.length) {
                g.log.debug('deactivating elements');
                activeOut.forEach(function (a) {
                    index = activeElements.indexOf(a);
                    if (index > -1) activeElements.splice(index, 1);
                    if (isCanvas(a))
                        a.reset();
                    else {
                        el = d3.select(a);
                        el.datum().reset().render(el);
                    }
                });
                paper.event('activeout').call(activeOut.splice(0));
            }

            activeIn.forEach(function (a) {
                index = activeElements.indexOf(a);
                if (index === -1) {
                    activeElements.push(a);
                    if (!isCanvas(a)) {
                        el = d3.select(a);
                        el.datum().highLight().render(el);
                    }
                }
            });

            activeElements.forEach(function (a) {
                if (isCanvas(a)) a.highLight().render();
            });

            //  clear activeIn array and if elements were available fire the
            //  ``active`` event on the paper
            if (activeIn.splice(0).length) {
                try {
                    paper.event('active').call(activeElements.slice());
                } catch (e) {
                    g.log.error('Exception while firing active event on giotto paper.\n' + e.stack);
                }
            }
        });


        g.constants.pointEvents.forEach(function (event) {

            paper.on(event, function () {
                var el = d3.select(this);
                if (el.size()) {
                    if (this.getContext) activeCanvas(paper, this.getContext('2d'));
                    else activeSvg(paper, el);
                }
            });
        });


        function activeSvg (paper, el) {
            var data = el.datum();
            if (!data || !data.highlighted)
                return paper.activeOut();

            var node = el.node();

            if (d3.event.type === 'mouseout')
                paper.activeOut(node);
            else if (d3.event.type === 'mouseout')
                paper.activeOut(node);
            else
                paper.activeIn(node);
        }

        function activeCanvas (paper, ctx) {
            var point = d3.canvas.mouse(ctx.canvas),
                active = paper.canvasDataAtPoint(point);

            if (canvases.indexOf(ctx) === -1) canvases.push(ctx);

            if (ctx.paperactive)
                ctx.paperactive.forEach(function (a) {
                    if (active.indexOf(a) === -1)
                        paper.activeOut(a);
                });
            ctx.paperactive = active.map(function (a) {
                paper.activeIn(a.context(ctx));
                return a;
            });
        }

        function isCanvas (a) {
            return isFunction(a.context);
        }
    }


    function chartFormats (group, opts, m) {
        if (!opts.formatX) opts.formatX = formatter(group.xaxis());
        if (!opts.formatY) opts.formatY = formatter(group.yaxis());
    }

    function formatter (axis) {
        var format = axis.tickFormat();
        if (!format) {
            format = axis.scale().tickFormat ? axis.scale().tickFormat(1000) : d3_identity;
        }
        return format;
    }

    //
    // Utility function to calculate paper dimensions and initialise the
    // paper options
    function _paperSize (element, p) {
        var width, height;

        if (isObject(element)) {
            p = element;
            element = null;
        }
        if (element && isFunction(element.node))
            element = element.node();
        if (!element)
            element = document.createElement('div');

        if (p) {
            if (p.__paper__ === element) return p;
            width = p.width;
            height = p.height;
        }
        else
            p = {};

        if (!width) {
            width = getWidth(element);
            if (width)
                p.elwidth = getWidthElement(element);
            else
                width = g.constants.WIDTH;
        }

        if (!height) {
            height = getHeight(element);
            if (height)
                p.elheight = getHeightElement(element);
            else
                height = g.constants.HEIGHT;
        }
        else if (typeof(height) === "string" && height.indexOf('%') === height.length-1) {
            p.height_percentage = 0.01*parseFloat(height);
            height = d3.round(p.height_percentage*width);
        }

        p.size = [width, height];
        p.giotto = 'giotto-group';

        element = d3.select(element);
        var position = element.style('position');
        if (!position || position === 'static')
            element.style('position', 'relative');
        p.__paper__ = element.node();

        return p;
    }

    //
    //  Defaults for Papers, Groups, Drawings and Visualizations

    g.defaults = {};

    g.defaults.paper = {
        type: 'svg',
        resizeDelay: 200,
        resize: true,
        interact: true,
        css: null
    };

    g.constants = {
        DEFAULT_VIZ_GROUP: 'default_viz_group',
        WIDTH: 400,
        HEIGHT: 300,
        vizevents: ['data', 'change', 'start', 'tick', 'end'],
        pointEvents: ["mouseenter", "mousemove", "touchstart", "touchmove", "mouseleave", "mouseout"],
        //
        // Events a giotto group can fire, added by pluigins
        groupEvents: [],
        //
        // leaflet url
        leaflet: 'http://cdn.leafletjs.com/leaflet-0.7.3/leaflet.css'
    };

    g.themes = {
        light: {},
        dark: {}
    };

    var ctheme = g.themes[theme] || g.themes.light;

    var _idCounter = 0;

    // Base giotto mixin for paper, group and viz
    function giottoMixin (d, opts, plugins) {
        var uid = ++_idCounter;

        opts = g.options(opts, plugins);

        // unique identifier for this object
        d.uid = function () {
            return uid;
        };

        d.event = function (name) {
            return noop;
        };

        //  Fire an event and return the mixin
        d.fire = function (name) {
            var event = d.event(name);
            event.call(d, {type: name});
            return d;
        };

        // returns the options object
        d.options = function (_) {
            if (!arguments.length) return opts;
            opts.extend(_);
            return d;
        };

        d.toString = function () {
            return 'giotto (' + uid + ')';
        };

        return d;
    }
    //
    //  Giotto Plugin Factory
    //  ==========================
    //
    //  Create a function for registering plugins for a given object ``main``
    function registerPlugin (main) {
        main.plugins = {};
        main.pluginArray = [];

        // Register a plugin
        //  - name: plugin name
        //  - plugin: plugin object
        main.plugin = function (name, plugin) {
            plugin = extend({}, defaultPlugin, plugin);
            plugin.name = name;
            // Overriding a plugin
            if (main.plugins[name]) {
                throw new Error('not implemented. Cannot override plugin');
            }
            main.plugins[name] = plugin;
            if (plugin.index !== undefined)
                main.pluginArray.splice(plugin.index, 0, plugin);
            else
                main.pluginArray.push(plugin);
        };

        return main;
    }

    //
    //	Giotto Options
    //	========================
    //
    //	Constructor of options for Giotto components
    g.options = function (opts, plugins) {
        // If this is not an option object create it
        if (!opts || !isFunction(opts.pluginOptions)) {

            var o = extend({}, g.defaults.paper);
                options = {};
            forEach(opts, function (value, name) {
                if (isPrivateAttribute(name)) o[name] = value;
                else options[name] = value;
            });
            opts = initOptions(o, {}).pluginOptions(plugins || g.paper.pluginArray).extend(options);
        } else if (plugins) {
            // Otherwise extend it with plugins given
            opts.pluginOptions(plugins);
        }
        return opts;
    };

    function isPrivateAttribute (name) {
        return name.substring(0, 1) === '_';
    }

    //
    //  Plugin base object
    //
    var defaultPlugin = {
        init: function () {},
        defaults: {},

        // Extend the plugin options
        extend: function (opts, value) {
            var name = this.name,
                defaults = opts[name],
                values = extend({}, defaults, value === true ? {show: true} : value);

            // deep copies
            forEach(this.deep, function (key) {
                values[key] = extend({}, opts[key], defaults[key], values[key]);
            });
            opts[name] = values;
        },

        clear: function (opts) {}
    };

    // Initialise options
    function initOptions (opts, pluginOptions) {

        // 	Extend public values of an option object with an object
        //	and return this options object.
        // 	A public value does not start with an underscore
        opts.extend = function (o) {
            var plugin, opn;

            // Loop through object values
            forEach(o, function (value, name) {
                // only extend non private values
                if (!isPrivateAttribute(name)) {
                    plugin = pluginOptions[name];
                    if (plugin)
                        plugin.extend(opts, value);
                    else
                        opts[name] = value;
                }
            });
            return opts;
        };

        //  If no argument is given, returns all plugins in this options object
        //  If a plugins object is given add plugins options only if plugins
        //  is not already available
        opts.pluginOptions = function (plugins) {
            if (!arguments.length) return pluginOptions;
            var name, o;

            if (plugins.length ) {
                var queue = [];

                forEach(plugins, function (plugin) {
                    if (pluginOptions[plugin.name] === undefined) {
                        pluginOptions[plugin.name] = plugin;
                        var value = opts[plugin.name];
                        opts[plugin.name] = plugin.defaults;
                        plugin.extend(opts, value);
                    }
                });
            }
            return opts;
        };

        // Copy this options object and return a new options object
        // with the same values apart from the one specified in ``o``.
        opts.copy = function (o) {
            if (o && isFunction(o.pluginOptions))
                return o;
            else
                return initOptions(extend({}, opts), extend({}, pluginOptions)).extend(o);
        };

        opts.clear = function () {
            forEach(pluginOptions, function (plugin) {
                plugin.clear(opts[plugin.name]);
            });
        };

        opts.selectTheme = function (theme) {
            var ctheme = g.themes[theme],
                obj;
            forEach(ctheme, function (o, key) {
                obj = opts[key];
                if (obj)
                    forEach(o, function (value, name) {
                        obj[name] = value;
                    });
            });
        };

        return opts;
    }

    //
    //  Gradient
    //  =============
    //
    //  Manage gradient information for both svg and canvas
    g.gradient = function () {
        var colors = [{
                color: '#000',
                opacity: 1,
                offset: 0
            },
            {
                color: '#fff',
                opacity: 1,
                offset: 100
            }],
            x1 = 0,
            x2 = 200,
            y1 = 0,
            y2 = 200,
            direction = 'y',
            type = 'linear';

        function gradient (g) {
            g.each(function () {
                if (this.tagName.toLowerCase() === 'canvas') {
                    var ctx = this.getContext('2d');
                    type === 'linear' ? linear_canvas(ctx) : radial_canvas(ctx);
                } else {
                    var el = d3.select(this),
                        id = giotto_id(el),
                        gid = 'grad-' + id,
                        defs = svg_defs(el);

                    defs.select('#' + gid).remove();
                    var grad = type === 'linear' ? linearsvg(defs) : radialsvg(defs);
                    grad.attr('id', gid);
                    el.attr('fill', 'url(#' + gid + ')');
                }
            });
        }

        function linearsvg (svg) {
            var grad = svg.append('linearGradient')
                            .attr('x1', '0%')
                            .attr('y1', '0%');

            if (direction === 'x')
                grad.attr('x2', '100%')
                    .attr('y2', '0%');
            else
                grad.attr('y2', '100%')
                    .attr('x2', '0%');

            colors.forEach(function (c) {
                grad.append("stop")
                    .attr("offset", c.offset+"%")
                    .attr("stop-color", c.color)
                    .attr("stop-opacity", c.opacity === undefined ? 1 : c.opacity);
            });

            return grad;
        }

        function linear_canvas (ctx) {
            var grad;
            if (direction === 'x')
                grad = ctx.createLinearGradient(x1, y1, x2, y1);
            else
                grad = ctx.createLinearGradient(x1, y1, x1, y2);
            colors.forEach(function (c) {
                grad.addColorStop(0.01*c.offset, c.color);
            });
            ctx.fillStyle = grad;
            ctx.fill();
        }

        gradient.direction = function (_) {
            if (!arguments.length) return direction;
            direction = _;
            return gradient;
        };

        gradient.colors = function (_) {
            if (!arguments.length) return colors;
            var step = 100/_.length;
            colors = _.map(function (c, i) {
                if (isString(c)) c = {color: c};
                if (c.offset === undefined) c.offset = Math.round(step*i);
                return c;
            });
            return gradient;
        };

        gradient.opacity = function (o) {
            colors.forEach(function (c) {c.opacity = o;});
            return gradient;
        };

        gradient.y1 = function (_) {
            if (!arguments.length) return y1;
            y1 = _;
            return gradient;
        };

        gradient.y2 = function (_) {
            if (!arguments.length) return y2;
            y2 = _;
            return gradient;
        };

        gradient.x1 = function (_) {
            if (!arguments.length) return x1;
            x1 = _;
            return gradient;
        };

        gradient.x2 = function (_) {
            if (!arguments.length) return x2;
            x2 = _;
            return gradient;
        };

        return gradient;
    };
    //
    // Create a new paper for drawing stuff
    g.paper = function (element, p) {

        var events = d3.dispatch.apply(null,
                extendArray(['change', 'active', 'activeout'], g.constants.pointEvents)),
            // Create the paper using giottoMixin
            paper = giottoMixin(d3.rebind({}, events, 'on'), p),
            tasks = [],
            resizing = false;

        p = _paperSize(element, paper.options());

        var type = p.type;

        element = p.__paper__;

        paper.event = function (name) {
            return events[name] || noop;
        };

        // Create a new group for this paper
        //	- opts: optional object with options for the new group
        paper.group = function (opts) {
            // Inject plugins
            opts = p.copy(opts);
            // Create the group
            var group = g.group[opts.type](paper, opts);

            group.element().classed(p.giotto, true);

            // apply plugins
            g.paper.pluginArray.forEach(function (plugin) {
                plugin.init(group);
            });

            return group;
        };

        paper.size = function () {
            return [p.size[0], p.size[1]];
        };

        // Select a group based on attributes
        paper.select = function (attr) {
            var selection = paper.svg().selectAll('.' + p.giotto),
                node;
            if (attr) selection = selection.filter(attr);
            node = selection.node();
            if (node) return node.__group__;
            selection = paper.canvas().selectAll('.' + p.giotto);
            if (attr) selection = selection.filter(attr);
            node = selection.node();
            if (node) return node.__group__;
        };

        paper.each = function (filter, callback) {
            if (arguments.length === 1) {
                callback = filter;
                filter = '*';
            }
            paper.svg().selectAll(filter).each(function () {
                if (this.__group__)
                    callback.call(this.__group__);
            });
            paper.canvas().selectAll(filter).each(function () {
                if (this.__group__)
                    callback.call(this.__group__);
            });
            return paper;
        };

        // Clear everything
        paper.clear = function () {
            paper.svg().remove();
            paper.canvas().remove();
            paper.canvasOverlay().remove();
            p.colorIndex = 0;
            return paper;
        };

        //  Remove tha paper.
        //  Nothing left after this operation
        paper.remove = function () {
            paper.element().remove();
        };

        paper.render = function () {
            var back = paper.canvasBackground().node(),
                over = paper.canvasOverlay().node(),
                c, i;
            if (back)
                d3.canvas.clear(back.getContext('2d'));
            if (over)
                d3.canvas.clear(over.getContext('2d'));
            if (p.fill)
                paper.element().style('background', p.fill);
            paper.each(function () {
                this.render();
            });
            return paper;
        };

        paper.element = function () {
            return d3.select(element);
        };

        paper.classGroup = function (cn, opts) {
            var gg = paper.select('.' + cn);
            if (!gg) {
                gg = paper.group(opts);
                gg.element().classed(cn, true);
            }
            return gg;
        };

        // Resize the paper and fire the resize event if resizing was performed
        paper.resize = function (size) {
            resizing = true;
            if (!size) size = paper.boundingBox();
            if (p.size[0] !== size[0] || p.size[1] !== size[1]) {
                p.size[0] = size[0];
                p.size[1] = size[1];
                paper.canvasOverlay();
                paper.canvasBackground(false, true);
                paper.each(function () {
                    this.resize();
                });
                events.change.call(paper, {type: 'change'});
            }
            resizing = false;
            return paper;
        };

        paper.boundingBox = function () {
            var w = p.elwidth ? getWidth(p.elwidth) : p.size[0],
                h;
            if (p.height_percentage)
                h = d3.round(w*p.height_percentage, 0);
            else
                h = p.elheight ? getHeight(p.elheight) : p.size[1];
            if (p.min_height)
                h = Math.max(h, p.min_height);
            return [Math.round(w), Math.round(h)];
        };

        // Create an svg container
        paper.svg = function (build) {
            var svg = paper.element().select('svg.giotto');
            if (!svg.node() && build)
                svg = paper.element().append('svg')
                                .attr('class', 'giotto')
                                .attr('width', p.size[0])
                                .attr('height', p.size[1]);
                if (!p.resize)
                    svg.attr("viewBox", "0 0 " + p.size[0] + " " + p.size[1]);
            return svg;
        };

        // Background svg group
        paper.svgBackground = function (build) {
            var svg = paper.svg();
            if (svg.size()) {
                var gr = svg.select('.giotto-background');
                if (!gr.size() && build)
                    gr = svg.insert('g', '*').classed('giotto-background', true);
                return gr;
            }
        };

        // Access the canvas container
        paper.canvas = function (build) {
            var canvas = paper.element().select('div.canvas-container');
            if (!canvas.node() && build) {
                canvas = paper.element().append('div')
                                .attr('class', 'canvas-container')
                                .style('position', 'relative');
            }
            return canvas;
        };

        // Access the canvas background
        paper.canvasBackground = function (build, clear) {
            var canvas = paper.canvas();

            if (canvas.size()) {
                var gr = canvas.select('.giotto-background'),
                    node = gr.node();
                if (!node && build) {
                    canvas.selectAll('*').style({"position": "absolute", "top": "0", "left": "0"});
                    gr = canvas.insert('canvas', '*').classed('giotto-background', true);
                    d3.canvas.retinaScale(gr.node().getContext('2d'), p.size[0], p.size[1]);
                }
                if (node && clear)
                    d3.canvas.resize(node.getContext('2d'), p.size[0], p.size[1]);
                return gr;
            }
            return canvas;
        };

        paper.canvasOverlay = function () {
            var canvas = paper.element().select('.canvas-overlay'),
                node = canvas.node();

            if (!node && paper.canvas().node()) {
                canvas = paper.element().append('canvas')
                                .attr('class', 'canvas-overlay')
                                .style({
                                    'position': 'absolute',
                                    'top': '0',
                                    'left': '0'
                                });
                node = canvas.node();
                d3.canvas.retinaScale(node.getContext('2d'), p.size[0], p.size[1]);
                paper.registerEvents(canvas, g.constants.pointEvents);
            } else if (node)
                d3.canvas.resize(node.getContext('2d'), p.size[0], p.size[1]);
            return canvas;
        };

        paper.canvasDataAtPoint = function (point) {
            var data = [];
            paper.canvas().selectAll('*').each(function () {
                if (this.__group__)
                    this.__group__.dataAtPoint(point, data);
            });
            return data;
        };

        paper.encodeSVG = function () {
            var svg = paper.svg();
            if (svg.node())
                return btoa(unescape(encodeURIComponent(
                    svg.attr("version", "1.1")
                        .attr("xmlns", "http://www.w3.org/2000/svg")
                        .node().parentNode.innerHTML)));
        };

        paper.imageSVG = function () {
            var svg = paper.encodeSVG();
            if (svg)
                return "data:image/svg+xml;charset=utf-8;base64," + svg;
        };

        paper.imagePNG = function () {
            var canvas = paper.canvas();
            if (!canvas.node()) return;

            var target = paper.group({
                    type: 'canvas',
                    margin: {left: 0, right: 0, top: 0, bottom: 0}
                }),
                ctx = target.context(),
                img, group;

            canvas.selectAll('*').each(function () {
                if (this.__group__ !== target) {
                    img = new Image();
                    img.src = this.getContext('2d').canvas.toDataURL();
                    ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height);
                }
            });
            var dataUrl = ctx.canvas.toDataURL();
            target.remove();
            return dataUrl;
        };

        paper.image = function () {
            return p.type === 'svg' ? paper.imageSVG() : paper.imagePNG();
        };


        // paper type
        paper.type = function () {
            return type;
        };
        //
        // register events on a DOM selection.
        paper.registerEvents = function (selection, events, uid, callback) {
            var target, ename;

            events.forEach(function (event) {
                ename = uid ? event + '.' + uid : event;

                selection.on(ename, function () {
                    if (uid && !paper.element().select('#' + uid).size())
                        // remove the event handler
                        selection.on(event + '.' + uid, null);
                    else {
                        target = callback ? callback.call(this) : this;
                        paper.event(d3.event.type).call(target);
                    }
                });
            });

            return selection;
        };
        //
        //  Add a new periodic task to the paper
        paper.task = function (callback) {
            tasks.push(callback);
        };
        //
        if (p.css)
            addCss('#giotto-paper-' + paper.uid(), p.css);

        // Auto resize the paper
        if (p.resize) {
            //
            d3.select(window).on('resize.paper' + paper.uid(), function () {
                if (!resizing) {
                    if (p.resizeDelay) {
                        resizing = true;
                        d3.timer(function () {
                            paper.resize();
                            return true;
                        }, p.resizeDelay);
                    } else {
                        paper.resize();
                    }
                }
            });
        }

        d3.timer(function () {
            if (!paper.element().size()) return true;
            for (var i=0; i<tasks.length; ++i) {
                tasks[i]();
            }
        });
        //
        activeEvents(paper);
        //
        return paper;
    };

    // Function to register plugin for papers
    registerPlugin(g.paper);

	//
	// 	group
	//	==================
	//
	//	A group is a container of a group of svg or canvas drawings.
	//	This function is never called directly, instead it is invoked by
	//	the ``paper.group()`` method.
	//		- paper: the paper creating this group
	//		- element: HTML element owning the new group
	//		- p: group parameters
    g.group = function (paper, element, p, _) {
        var drawings = [],
            factor = 1,
            rendering = false,
            resizing = false,
            type = p.type,
            d3v = d3[type],
            scale = d3.scale.linear(),
            events = d3.dispatch.apply(null, g.constants.groupEvents),
            group = giottoMixin(d3.rebind({}, events, 'on'), p);

        element.__group__ = group;
        p = group.options();

        // group type - svg or canvas
        group.type = function () {
            return type;
        };

        group.event = function (name) {
            return events[name] || noop;
        };

        group.element = function () {
            return d3.select(element);
        };

        group.paper = function () {
            return paper;
        };

        // [width, height] in pixels
        group.width = function () {
            return factor*p.size[0];
        };

        group.height = function () {
            return factor*p.size[1];
        };

        group.factor = function (x) {
            if (!arguments.length) return factor;
            factor = +x;
            return group;
        };

        group.size = function () {
            return [group.width(), group.height()];
        };

        group.add = function (draw) {
            if (isFunction(draw)) draw = drawing(group, draw);
            drawings.push(draw);
            return draw;
        };

        group.each = function (callback) {
            for (var i=0; i<drawings.length; ++i)
                callback.call(drawings[i]);
            return group;
        };

        group.render = function () {
            if (rendering) return;
            rendering = true;
            for (var i=0; i<drawings.length; ++i)
                drawings[i].render();
            rendering = false;
            return group;
        };

        group.rendering = function () {
            return rendering;
        };

        // remove this group from the paper or a drawing by name
        group.remove = function (name) {
            if (!arguments.lenght) {
                return group.element().remove();
            }
            var draw;
            for (var i=0; i<drawings.length; ++i) {
                draw = drawings[i];
                if (!name)
                    draw.remove();
                else if (draw.name() === name) {
                    draw.remove();
                    return drawings.splice(i, 1);
                }
            }
            return group;
        };

        group.resize = function (size) {
            resizing = true;
            _.resize(group, size);
            resizing = false;
            return group;
        };

        group.resizing = function () {
            return resizing;
        };

        group.scale = function (r) {
            if (!arguments.length) return scale;
            return scale(r);
        };

        group.fromPX = function (px) {
            return scale.invert(factor*px);
        };

        group.xfromPX = group.fromPX;
        group.yfromPX = group.fromPX;

        group.dim = function (x) {
            if (!x) return 0;

            var v = +x;
            // assume input is in pixels
            if (isNaN(v))
                return group.fromPX(x.substring(0, x.length-2));
            // otherwise assume it is a value between 0 and 1 defined as percentage of the x axis length
            else
                return v;
        };

        return group;
    };


    var drawingOptions = ['fill', 'fillOpacity', 'color', 'colorOpacity',
                          'lineWidth'];
    //
    // A drawing is drawn on a group by the renderer function
    function drawing (group, renderer, draw) {
        var uid = giotto_id(),
            x = d3_geom_pointX,
            y = d3_geom_pointY,
            opts = {},
            pointOptions = drawingOptions,
            size = function (d) {return d.size;},
            changed,
            name,
            data,
            formatX,
            formatY,
            label,
            dataConstructor,
            set;

        draw = highlightMixin(draw);
        set = draw.set;

        draw.uid = function () {
            return uid;
        };

        draw.remove = noop;

        draw.render = function () {
            if (renderer)
                return renderer.apply(draw);
        };

        draw.group = function () {
            return group;
        };

        draw.draw = function () {
            return draw;
        };

        draw.each = function (callback) {
            if (data)
                data.forEach(function (d) {
                    callback.call(d);
                });
            else
                callback.call(draw);
            return draw;
        };

        draw.renderer = function (_) {
            if (arguments.length === 0) return renderer;
            renderer = _;
            return draw;
        };

        draw.options = function (_) {
            if (arguments.length === 0) return opts;
            opts = _;
            if (isFunction(opts.x)) draw.x(opts.x);
            if (isFunction(opts.y)) draw.y(opts.y);
            if (opts.formatX) formatX = _format(opts.formatX);
            if (opts.formatY) formatY = _format(opts.formatY);
            draw.init(draw, opts);
            return draw;
        };

        // set a value and its default (override highlight)
        draw.set = function (name, value) {
            opts[name] = value;
            set(name, value);
            if (data && pointOptions.indexOf(name) > -1) {
                data.forEach(function (d) {
                    d.set(name, value);
                });
            }
            return draw;
        };

        draw.x = function (_) {
            if (arguments.length === 0) return x;
            x = d3_functor(_);
            return draw;
        };

        draw.y = function (_) {
            if (arguments.length === 0) return y;
            y = d3_functor(_);
            return draw;
        };

        draw.formatX = function (x) {
            if (!formatX) formatX = d3.format('n');
            return formatX(x);
        };

        draw.formatY = function (y) {
            if (!formatY) formatY = d3.format('n');
            return formatY(y);
        };

        draw.size = function (_) {
            if (arguments.length === 0) return size;
            size = d3_functor(_);
            return draw;
        };

        draw.name = function (_) {
            if (arguments.length === 0) return name;
            name = _;
            return draw;
        };

        draw.scalex = function () {
            var scalex = group.xaxis().scale();
            return function (d) {
                return scalex(x(d));
            };
        };

        draw.scaley = function () {
            var scaley = group.yaxis().scale();
            return function (d) {
                return scaley(y(d));
            };
        };

        draw.add = function (d) {
            if (dataConstructor)
                d = dataConstructor.call(draw, [d]);
            if (data)
                data.push(d[0]);
            else
                data = d;
            return draw;
        };

        // replace the data for this drawing
        draw.data = function (_) {
            if (!arguments.length) return data;
            changed = true;
            if (dataConstructor)
                data = dataConstructor.call(draw, _);
            else
                data = _;
            return draw;
        };

        draw.changed = function () {
            var c = changed;
            changed = false;
            return c;
        };

        draw.dataConstructor = function (_) {
            if (!arguments.length) return dataConstructor;
            dataConstructor = d3_functor(_);
            return draw;
        };

        draw.label = function (_) {
            if (!arguments.length) return label;
            label = _;
            return draw;
        };

        draw.pointOptions = function (_) {
            if (!arguments.length) return pointOptions;
            pointOptions = _;
            return draw;
        };

        return draw;

        function _set(name, value) {
            if (typeof draw[name] === 'function')
                draw[name](value);
            else
                draw[name] = value;
        }

        function _format (format) {
            return isFunction(format) ? format : d3.format(format);
        }
    }

    // A mixin for highlighting elements
    //
    // This is used by the drawing and drawingData constructors
    function highlightMixin (d) {
        var values = {},
            opts,
            highlight = false;

        d || (d = {});

        d.factor = function () {
            return d.group().factor();
        };

        d.paper = function () {
            return d.group().paper();
        };

        d.highLight = function () {
            if (highlight) return d;

            var a = d.active,
                v;
            if (a) {
                highlight = true;
                d.pointOptions().forEach(function (name) {
                    v = a[name];
                    if (v) {
                        if (typeof v === 'string') {
                            if (v === 'darker')
                                v = d3.rgb(values[name]).darker();
                            else if (v === 'brighter')
                                v = d3.rgb(values[name]).brighter();
                            else if (v.substring(v.length-1) === '%')
                                v = 0.01 * v.substring(0,v.length-1) * values[name];
                        }
                        d[name] = v;
                    }
                });
            }
            return d;
        };

        d.highlighted = function () {
            return highlight;
        };

        // set a value and its default
        d.set = function (name, value) {
            if (d.pointOptions().indexOf(name) > -1) {
                values[name] = value;
                d[name] = value;
            }
            return d;
        };

        d.reset = function () {
            highlight = false;
            d.pointOptions().forEach(function (name) {
                d[name] = values[name];
            });
            return d;
        };

        d.init = function (data, opts, dd) {
            var value;
            d.pointOptions().forEach(function (name) {
                value = data[name] || opts[name];
                if (isFunction(value) && dd) value = value(dd);
                values[name] = value;
            });
            if (opts.active && d.active !== false) {
                if (!data.active)
                    data.active = {};
                copyMissing(opts.active, data.active);
            }
            return d.reset();
        };

        d.setBackground = function (e) {
            d.group().setBackground(d, e);
            return d;
        };

        d.inRange = noop;

        return d;
    }
    //
    // Manage a data point to be drawn on a drawing collection
    function drawingData (draw, data, d) {
        var opts = draw.options();
        d = highlightMixin(d);
        d.data = data;

        d.options = function () {
            return opts;
        };

        d.draw = function () {
            return draw;
        };

        d.group = function () {
            return draw.group();
        };

        d.pointOptions = function () {
            return draw.pointOptions();
        };

        if (!data || isArray(data))
            d.init(d, opts);
        else {
            d.init(data, opts, data);
            d.active = data.active;
        }

        return d;
    }

    //
    //  SVG group
    //  ================
    g.group.svg = function (paper, p) {
        var container = paper.svg(true),
            elem = p.before ? container.insert('g', p.before) : container.append('g'),
            _ = {};

        delete p.before;

        _.resize = function (group) {
            if (p.resize) {
                paper.svg()
                    .attr('width', p.size[0])
                    .attr('height', p.size[1]);
                group.resetAxis().render();
            }
        };

        var group = g.group(paper, elem.node(), p, _),
            render = group.render;

        group.render = function () {
            group.element().attr("transform", "translate(" + group.marginLeft() + "," + group.marginTop() + ")");
            return render();
        };

        group.clear = function () {
            group.element().selectAll('*').remove();
            return group;
        };

        group.draw = function (selection) {
            return selection
                .attr('stroke', function (d) {return d.color;})
                .attr('stroke-opacity', function (d) {return d.colorOpacity;})
                .attr('stroke-width', function (d) {return d.lineWidth;})
                .attr('fill', function (d) {return d.fill;})
                .attr('fill-opacity', function (d) {return d.fill === 'none' ? undefined : d.fillOpacity;});
        };

        group.events = function (selection, uid, callback) {
            return paper.registerEvents(selection, g.constants.pointEvents, uid, callback);
        };

        return group;
    };

    function svg_font (selection, opts) {
        return selection
            .attr('fill', opts.color)
            .style({
                'font-size': opts.size ,
                'font-weight': opts.weight,
                'font-style': opts.style,
                'font-family': opts.family,
                'font-variant': opts.variant
            });
    }

    g.svg.font = function (selection, opts) {
        opts = extend({}, g.defaults.paper.font, opts);
        return svg_font(selection, opts);
    };

    //
    //  Canvas
    //  ======================
    g.group.canvas = function (paper, p) {

        var container = paper.canvas(true),
            elem = p.before ? container.insert('canvas', p.before) : container.append('canvas'),
            ctx = elem.node().getContext('2d'),
            _ = {};

        delete p.before;
        container.selectAll('*').style({"position": "absolute", "top": "0", "left": "0"});
        container.select('*').style({"position": "relative"});

        _.scale = function (group) {
            return d3.canvas.retinaScale(group.context(), p.size[0], p.size[1]);
        };

        _.resize = function (group) {
            d3.canvas.clear(group.context());
            _.scale(group);
            group.resetAxis().render();
        };

        var group = g.group(paper, elem.node(), p, _),
            render = group.render;

        group.render = function () {
            d3.canvas.clear(ctx);
            return render();
        };

        // clear the group without removing drawing from memory
        group.clear = function () {
            d3.canvas.clear(ctx);
            return group;
        };

        group.context = function () {
            return ctx;
        };

        group.dataAtPoint = function (point, elements) {
            var x = point[0],
                y = point[1],
                active,
                data;
            group.each(function () {
                this.each(function () {
                    active = this.inRange(x, y);
                    if (active === true) elements.push(this);
                    else if (active) elements.push(active);
                });
            });
        };

        group.transform = function (ctx) {
            ctx.setTransform(1, 0, 0, 1, 0, 0);
            ctx.translate(group.marginLeft(), group.marginTop());
            return group;
        };

        return group.factor(_.scale(group));
    };

    g.canvas.font = function (ctx, opts) {
        opts = extend({}, g.defaults.paper.font, opts);
        ctx.fillStyle = opts.color;
        ctx.font = fontString(opts);
    };

    function canvasMixin(d) {
        var ctx,
            reset = d.reset,
            group = d.group();

        d.inRange = function () {};

        d.bbox = function () {};

        d.reset = function () {
            ctx = group.context();
            return reset.call(d);
        };

        d.context = function (_) {
            if (!arguments.length) return ctx;
            ctx = _;
            return d;
        };

        return d;
    }

    function canvasBBox (d, nw, ne, se, sw) {
        var target = d.paper().element().node(),
            bbox = target.getBoundingClientRect(),
            p = [bbox.left, bbox.top],
            f = 1/d3.canvas.pixelRatio;
        return {
            nw: {x: f*nw[0] + p[0], y: f*nw[1] + p[1]},
            ne: {x: f*ne[0] + p[0], y: f*ne[1] + p[1]},
            se: {x: f*se[0] + p[0], y: f*se[1] + p[1]},
            sw: {x: f*sw[0] + p[0], y: f*sw[1] + p[1]},
            n: {x: av(nw, ne, 0), y: av(nw, ne, 1)},
            s: {x: av(sw, se, 0), y: av(sw, se, 1)},
            e: {x: av(se, ne, 0), y: av(se, ne, 1)},
            w: {x: av(sw, nw, 0), y: av(sw, nw, 1)}
        };

        function av(a, b, i) {return p[i] + 0.5*f*(a[i] + b[i]);}
    }

    //
    // Namespace for all visualizations
    g.viz = {};
    //
    // Plugins for all visualization classes
    registerPlugin(g.viz);
    //
    //  Factory of Giotto visualization factories
    //  =============================================
    //
    //  name: name of the visualization constructor, the constructor is
    //        accessed via the giotto.viz object
    //  defaults: object of default parameters
    //  constructor: function called back with a visualization object
    //               and an object containing options for the visualization
    //  returns a functyion which create visualization of the ``name`` family
    g.createviz = function (name, defaults, constructor) {

        (defaults || (defaults={}));

        // The visualization factory
        var

        withPaper = defaults.paper === undefined ? true : defaults.paper,

        // The vizualization constructor
        vizType = function (element, p) {

            if (isObject(element)) {
                p = element;
                element = null;
            }

            var vizPlugins = extendArray([], g.viz.pluginArray, vizType.pluginArray),
                allPlugins = extendArray([], g.paper.pluginArray, vizPlugins),
                viz = giottoMixin({}, vizType.defaults, allPlugins).options(p),
                events = d3.dispatch.apply(d3, g.constants.vizevents),
                alpha = 0,
                paper;

            viz.event = function (name) {
                return events[name] || noop;
            };

            // Return the visualization type (a function)
            viz.vizType = function () {
                return vizType;
            };

            viz.vizName = function () {
                return vizType.vizName();
            };

            // Starts the visualization
            viz.start = function () {
                return onInitViz(viz).load(viz.resume);
            };

            // Add paper functionalities
            if (withPaper) {

                viz.paper = function (createNew) {
                    if (createNew || paper === undefined) {
                        if (paper) {
                            paper.clear();
                            viz.options().clear();
                        }
                        paper = viz.createPaper();
                    }
                    return paper;
                };

                viz.createPaper = function () {
                    return g.paper(element, viz.options());
                };

                viz.element = function () {
                    return viz.paper().element();
                };

                viz.clear = function () {
                    viz.paper().clear();
                    return viz;
                };

                viz.alpha = function(x) {
                    if (!arguments.length) return alpha;

                    x = +x;
                    if (alpha) { // if we're already running
                        if (x > 0) alpha = x; // we might keep it hot
                        else alpha = 0; // or, next tick will dispatch "end"
                    } else if (x > 0) { // otherwise, fire it up!
                        events.start({type: "start", alpha: alpha = x});
                        d3.timer(viz.tick);
                    }

                    return viz;
                };

                viz.resume = function() {
                    return viz.alpha(0.1);
                };

                viz.stop = function() {
                    return viz.alpha(0);
                };

                viz.tick = function() {
                    // simulated annealing, basically
                    if ((alpha *= 0.99) < 0.005) {
                        events.end({type: "end", alpha: alpha = 0});
                        return true;
                    }
                    events.tick({type: "tick", alpha: alpha});
                };

                // render the visualization by invoking the render method of the paper
                viz.render = function () {
                    paper.render();
                    return viz;
                };

                viz.image = function () {
                    return paper.image();
                };
            }

            d3.rebind(viz, events, 'on');

            // If constructor available, call it first
            if (constructor)
                constructor(viz);

            // Inject plugins
            vizPlugins.forEach(function (plugin) {
                plugin.init(viz);
            });

            return viz;
        };

        delete defaults.paper;

        g.viz[name] = vizType;

        vizType.defaults = defaults;

        vizType.vizName = function () {
            return name;
        };

        registerPlugin(vizType);

        return vizType;
    };

    g.createviz('viz');

    function onInitViz(viz, init) {
        if (!viz.__init__) {
            viz.__init__ = true;
            if (init) init();

            var opts = viz.options();
            // if the onInit callback available, execute it
            if (opts.onInit) {
                init = getObject(opts.onInit);

                if (isFunction(init))
                    init(viz, opts);
                else
                    g.log.error('Could not locate onInit function ' + opts.onInit);
            }
        }
        return viz;
    }

    //
    //  Font
    //  ===============
    //
    //  Add fonts to a giotto group
    //
    g.paper.plugin('font', {

        defaults: {
            color: '#444',
            size: '11px',
            weight: 'normal',
            lineHeight: 13,
            style: "normal",
            family: "sans-serif",
            variant: "small-caps"
        }
    });

    //
    //  Margin plugin
    //  ================
    //
    //
    //  Margin
    //  ===========
    //
    //  Add margins to a giotto group
    //
    g.paper.plugin('margin', {

        defaults: {
            top: 20,
            right: 20,
            bottom: 20,
            left: 20
        },

        init: function (group) {

            var p = group.options(),
                factor = group.factor();

            group.marginLeft = function () {
                return factor*pc(p.margin.left, p.size[0]);
            };

            group.marginRight = function () {
                return factor*pc(p.margin.right, p.size[0]);
            };

            group.marginTop = function () {
                return factor*pc(p.margin.top, p.size[1]);
            };

            group.marginBottom = function () {
                return factor*pc(p.margin.bottom, p.size[1]);
            };

            group.innerWidth = function () {
                return factor*p.size[0] - group.marginLeft() - group.marginRight();
            };

            group.innerHeight = function () {
                return factor*p.size[1] - group.marginTop() - group.marginBottom();
            };

            group.aspectRatio = function () {
                return group.innerHeight()/group.innerWidth();
            };

            function pc (margin, size) {
                if (typeof(margin) === "string" && margin.indexOf('%') === margin.length-1)
                    margin = d3.round(0.01*parseFloat(margin)*size, 5);
                return margin;
            }
        },

        options: function (opts) {
            var margin = opts.margin;
            opts.margin = extend({}, this.defaults);
            this.extend(opts.margin, margin);
        },

        // Allow to specify margin as a scalar value
        extend: function (opts, value) {
            if (value === undefined)
                return;
            if (!isObject(value))
                value = {
                    left: value,
                    right: value,
                    top: value,
                    bottom: value
                };
            else
                value = extend({}, opts[this.name], value);
            opts[this.name] = value;
        }
    });

    //
    //  Transition
    //  ===============
    //
    //  Transitions values for all plugins needing one
    g.paper.plugin('transition', {

        defaults: {
            duration: 0,
            ease: 'easeInOutCubic'
        }
    });
    var tooltip;
    //
    //  Tooltip functionality
    g.paper.plugin('tooltip', {
        deep: ['font', 'transition'],

        defaults: {
            className: 'd3-tip',
            fill: '#deebf7',
            fillOpacity: 0.8,
            color: '#222',
            padding: '8px',
            radius: '3px',
            offset: [20, 20],
            template: function (d) {
                return "<p><span style='color:"+d.c+"'>" + d.l + "</span>  <strong>" +
                        d.x + ": </strong><span>" + d.y + "</span></p>";
            },
            font: {
                size: '14px'
            }
        },

        init: function (group) {
            var paper = group.paper();
            if (!paper.showTooltip) activateTooltip(paper);
        }
    });


    function activateTooltip (paper) {
        var opts = paper.options(),
            tooltip;

        paper.showTooltip = function () {
            if (!tooltip) tooltip = gitto_tip(opts).offset(opts.tooltip.offset);
            show();
            return paper;
        };

        paper.hideTooltip = function () {
            if (tooltip) tooltip.hide();
            return paper;
        };

        paper.removeTooltip = function () {
            if (tooltip) tooltip.hide();
            opts.tooltip.show = false;
            tooltip = null;
            return paper;
        };

        paper.on('active.tooltip', function () {
            if (tooltip) {
                tooltip.active = this;
                show();
            }
        }).on('activeout.tooltip', function () {
            if (tooltip) {
                tooltip.active.splice(0);
                tooltip.hide();
            }
        });

        //paper.task(function () {
        //    if (opts.tooltip.show) show();
        //});

        if (opts.tooltip.show) paper.showTooltip();

        function show () {
            var active = tooltip.active;
            if (!active.length) return tooltip.hide();

            var bbox = getBbox(active[0]),
                direction = bbox.tooltip || 'n';
            if (active.length > 1) {
                direction = 'e';
                for (var i=1; i<active.length; ++i) {
                    var bbox2 = getBbox(active[i]);
                    bbox[direction].y += bbox2[direction].y;
                }
                bbox[direction].y /= active.length;
            }
            tooltip.bbox(bbox).direction(direction).show();
        }

        function getBbox (node) {
            if (isFunction(node.bbox)) return node.bbox();
            else return getScreenBBox(node);
        }
    }


    function gitto_tip (options) {
        var opts = options.tooltip,
            font = extend({}, options.font, opts.font),
            tip = g.tip();

        tip.active = [];

        tip.attr('class', opts.className)
           .style({
                background: opts.fill,
                opacity: opts.fillOpacity,
                color: opts.color,
                padding: opts.padding,
                'border-radius': opts.radius,
                font: fontString(font)
            });

        if (opts.className === 'd3-tip' && tooltipCss) {
            tooltipCss['d3-tip:after'].color = opts.fill;
            addCss('', tooltipCss);
            tooltipCss = null;
        }

        tip.html(function () {
            var html = '',
                data, draw, template;

            for (var i=0; i<tip.active.length; ++i) {
                data = tip.active[i];
                if (!data.draw) data = d3.select(data).datum();
                draw = data.draw();
                template = tooltip_template(draw);

                html += template({
                    c: data.color,
                    l: draw.label()(data.data) || 'serie',
                    x: draw.formatX(draw.x()(data.data)),
                    y: draw.formatY(draw.y()(data.data))
                });
            }
            return html;
        });

        return tip;

        function tooltip_template (draw) {
            var o = draw.options();
            return o.tooltip ? o.tooltip.template || opts.template : opts.template;
        }
    }

    //
    // Returns a tip handle
    g.tip = function () {

        var direction = d3_tip_direction,
            offset = [0, 0],
            html = d3_tip_html,
            node = initNode(),
            tip = {},
            bbox;

        document.body.appendChild(node);

        // Public - show the tooltip on the screen
        //
        // Returns a tip
        tip.show = function () {
            var content = html.call(tip),
                dir = direction.call(tip),
                nodel = d3.select(node),
                i = directions.length,
                coords,
                scrollTop = document.documentElement.scrollTop || document.body.scrollTop,
                scrollLeft = document.documentElement.scrollLeft || document.body.scrollLeft;

            nodel.html(content)
                .style({
                opacity: 1,
                'pointer-events': 'all'
            });

            while (i--)
                nodel.classed(directions[i], false);

            coords = direction_callbacks.get(dir).apply(this);
            nodel.classed(dir, true).style({
                top: coords.top + scrollTop + 'px',
                left: coords.left + scrollLeft + 'px'
            });
            return tip;
        };

        // Public - hide the tooltip
        //
        // Returns a tip
        tip.hide = function() {
            d3.select(node).style({
                opacity: 0,
                'pointer-events': 'none'
            });
            return tip;
        };

        // Public: Proxy attr calls to the d3 tip container.  Sets or gets attribute value.
        //
        // n - name of the attribute
        // v - value of the attribute
        //
        // Returns tip or attribute value
        tip.attr = function(n, v) {
            if (arguments.length < 2 && typeof n === 'string') {
                return d3.select(node).attr(n);
            } else {
                var args = Array.prototype.slice.call(arguments);
                d3.selection.prototype.attr.apply(d3.select(node), args);
            }
            return tip;
        };

        // Public: Proxy style calls to the d3 tip container.  Sets or gets a style value.
        //
        // n - name of the property
        // v - value of the property
        //
        // Returns tip or style property value
        tip.style = function(n, v) {
            if (arguments.length < 2 && typeof n === 'string') {
                return d3.select(node).style(n);
            } else {
                var args = Array.prototype.slice.call(arguments);
                d3.selection.prototype.style.apply(d3.select(node), args);
            }
            return tip;
        };

        tip.bbox = function (x) {
            if (!arguments.length) return bbox;
            bbox = x;
            return tip;
        };

        // Public: Set or get the direction of the tooltip
        //
        // v - One of n(north), s(south), e(east), or w(west), nw(northwest),
        //     sw(southwest), ne(northeast) or se(southeast)
        //
        // Returns tip or direction
        tip.direction = function (v) {
            if (!arguments.length) return direction;
            direction = v === null ? v : d3.functor(v);
            return tip;
        };

        // Public: Sets or gets the offset of the tip
        //
        // v - Array of [x, y] offset
        //
        tip.offset = function (v) {
            if (!arguments.length) return offset;
            offset = v;
            return tip;
        };

        // Public: sets or gets the html value of the tooltip
        //
        // v - String value of the tip
        //
        // Returns html value or tip
        tip.html = function (v) {
            if (!arguments.length) return html;
            html = v === null ? v : d3.functor(v);
            return tip;
        };

        function d3_tip_direction () {
            return 'n';
        }

        function d3_tip_html() {
            return ' ';
        }

        var direction_callbacks = d3.map({
            n: direction_n,
            s: direction_s,
            e: direction_e,
            w: direction_w,
            nw: direction_nw,
            ne: direction_ne,
            sw: direction_sw,
            se: direction_se,
            c: direction_c
        }),

        directions = direction_callbacks.keys();

        function direction_n () {
            return {
                top: bbox.n.y - node.offsetHeight - offset[1],
                left: bbox.n.x - node.offsetWidth / 2
            };
        }

        function direction_s () {
            return {
                top: bbox.s.y + offset[1],
                left: bbox.s.x - node.offsetWidth / 2
            };
        }

        function direction_e () {
            return {
                top: bbox.e.y - node.offsetHeight / 2,
                left: bbox.e.x + offset[0]
            };
        }

        function direction_w () {
            return {
                top: bbox.w.y - node.offsetHeight / 2,
                left: bbox.w.x - node.offsetWidth - offset[0]
            };
        }

        function direction_nw () {
            return {
                top: bbox.nw.y - node.offsetHeight - offset[1],
                left: bbox.nw.x - node.offsetWidth - offset[0]
            };
        }

        function direction_ne () {
            return {
                top: bbox.ne.y - node.offsetHeight - offset[1],
                left: bbox.ne.x + offset[0]
            };
        }

        function direction_sw () {
            return {
                top: bbox.sw.y + offset[1],
                left: bbox.sw.x - node.offsetWidth - offset[0]
            };
        }

        function direction_se () {
            return {
                top: bbox.se.y + offset[1],
                left: bbox.e.x + offset[0]
            };
        }

        function direction_c () {
            return {
                top: bbox.c.y + offset[1],
                left: bbox.c.x + offset[0]
            };
        }

        function initNode() {
            var node = d3.select(document.createElement('div'));
            node.style({
                position: 'absolute',
                top: 0,
                opacity: 0,
                'pointer-events': 'none',
                'box-sizing': 'border-box'
            });
            return node.node();
        }

        return tip;
    };


    var tooltipCss = {'d3-tip:after': {}};


    g.createviz('chart', {
        margin: 30,
        chartTypes: ['geo', 'pie', 'bar', 'line', 'point', 'custom'],
        xaxis: {
            show: true
        },
        yaxis: {
            show: true
        },
        serie: {
            x: function (d) {return d[0];},
            y: function (d) {return d[1];}
        }
    },

    function (chart) {

        var series = [],
            allranges = {},
            drawing;

        chart.numSeries = function () {
            return series.length;
        };

        chart.allranges = function () {
            return allranges;
        };

        // iterator over each serie
        chart.each = function (callback) {
            series.forEach(callback);
            return chart;
        };

        chart.forEach = chart.each;

        chart.addSeries = function (series) {
            addSeries(series);
            return chart;
        };

        chart.addSerie = function (serie) {
            addSeries([serie]);
            return chart;
        };

        chart.clear = function () {
            chart.paper().clear();
            series = [];
            return chart;
        };

        chart.drawing  = function () {
            return drawing;
        };

        chart.render = function () {
            var opts = chart.options(),
                paper = chart.paper();
            drawing = true;

            if (opts.type !== paper.type()) {
                paper = chart.paper(true);
                chart.each(function (serie) {
                    serie.clear();
                });
            }

            chart.each(function (serie) {
                serie.draw();
            });

            drawing = false;

            // Render the chart
            paper.render();
            return chart;
        };

        chart.setSerieOption = function (type, field, value) {
            var opts = chart.options();
            if (opts.chartTypes.indexOf(type) === -1) return;

            if (!chart.numSeries()) {
                opts[type][field] = value;
            } else {
                var stype;
                chart.each(function (serie) {
                    stype = serie[type];
                    if (stype)
                        if (isFunction(stype.set))
                            stype.set(field, value);
                        else
                            stype[field] = value;
                });
            }
        };

        // Return the giotto group which manage the axis for a serie
        chart.axisGroup = function (serie) {
            if (serie && serie.axisgroup)
                return chart.paper().select('.' + chart.axisGroupId(serie.axisgroup));
        };


        chart.on('tick.main', function () {
            // Chart don't need ticking unless explicitly required (real time updates for example)
            chart.stop();
            chart.render();
        });

        chart.axisGroupId = function (axisgroup) {
            return 'axisgroup' + chart.uid() + '-' + axisgroup;
        };

        // INTERNALS

        chart.on('data.build_series', function () {
            var data = chart.data();
            series = [];
            addSeries(data);
        });

        g.chartContextMenu(chart);

        function addSeries (newseries) {
            // Loop through series and add them to the chart series collection
            // No drawing nor rendering involved
            if (!newseries.forEach) newseries = [newseries];

            newseries.forEach(function (serie) {

                if (isFunction(serie))
                    serie = serie(chart);

                series.push(chartSerie(chart, serie));
            });
        }

    });

    g.chart = g.viz.chart;


    g.chartContextMenu = function (chart) {

        var menu = [];
        chart.options().menu.items = menu;

        menu.push({
            label: 'Open Image',
            callback: function (chart) {
                    window.open(chart.image());
            }
        },
        {
            label: function () {
                if (chart.paper().type() === 'svg')
                    return 'Redraw as Canvas';
                else
                    return 'Redraw as SVG';
            },
            callback: function () {
                var type = 'svg';
                if (chart.paper().type() === 'svg')
                    type = 'canvas';
                chart.options().type = type;
                chart.resume();
            }
        });
    };
    //
    //	Create a serie for a chart
    //  ================================
    //
    //  Return a giotto.data.serie object with chart specific functions
    //
    //  A Chart serie create a new giotto group where to draw the serie which
    //  can be a univariate (x,y) or multivariate (x, y_1, y_2, ..., y_n)
    function chartSerie (chart, data) {

        if (!data) return;

        var serie = data,
            obj;

        // If data does not have the forEach function, extend the serie with it
        // and data is obtained from the serie data attribute
        if (!isFunction(data.forEach)) {
            obj = data;
            data = obj.data;
            delete obj.data;
        } else
            obj = {};

        // if not a serie object create the serie
        if (!data || isArray(data))
            serie = g.data.serie().data(data);
        else {
            serie = data;
            data = null;
        }

        if (obj.label) {
            serie.label(d3_functor(obj.label));
            delete obj.label;
        }

        serie.index = chart.numSeries();

        //  Add label if not available
        if (!serie.label()) serie.label(d3_functor('serie ' + serie.index));

        _extendSerie(chart, serie, obj);

        return serie.data(serie.data());
    }


    function _extendSerie (chart, serie, groupOptions) {

        var opts = chart.options(),
            allranges = chart.allranges(),
            serieData = serie.data,
            drawXaxis = false,
            drawYaxis = false,
            group, color, show, scaled;

        opts.chartTypes.forEach(function (type) {
            var o = groupOptions[type];
            if (o || (opts[type] && opts[type].show)) {
                serie[type] = extend({}, opts[type], o);
                show = true;
                // Could be a function
                if (!serie[type].show)
                    serie[type].show = true;
            }
        });

        // None of the chart are shown, specify line
        if (!show)
            serie.line = extend({}, opts.line, {show: true});

        opts.chartTypes.forEach(function (type) {
            var o = serie[type];

            if (o && chartTypes[type].scaled) {
                // pick a default color if one is not given
                if (!color)
                    color = chart.drawColor(o);
                if (!o.color)
                    o.color = color;
                scaled = true;
            }
        });

        // The serie needs axis
        if (scaled) {
            if (serie.yaxis === undefined)
                serie.yaxis = 1;
            if (!serie.axisgroup) serie.axisgroup = 1;

            var ranges = allranges[serie.axisgroup];

            if (!ranges) {
                // ranges not yet available for this chart axisgroup,
                // mark the serie as the reference for this axisgroup
                serie.reference = true;
                allranges[serie.axisgroup] = ranges = {};
            }

            if (!isObject(serie.xaxis)) serie.xaxis = opts.xaxis;
            if (serie.yaxis === 2) serie.yaxis = opts.yaxis2;
            if (!isObject(serie.yaxis)) serie.yaxis = opts.yaxis;
        }

        // The group of this serie
        serie.group = function () {
            return group;
        };

        serie.clear = function () {
            if (group) group.remove();
            group = null;
            return serie;
        };

        //  Override data function
        serie.data = function (inpdata) {
            if (!arguments.length) return serieData();
            serieData(inpdata);

            // check axis and ranges
            if (scaled) {
                drawXaxis = setRange(serie.xaxis.position, serie.xrange());
                drawYaxis = setRange(serie.yaxis.position, serie.yrange());
            }

            opts.chartTypes.forEach(function (type) {
                stype = serie[type];
                if (stype && isFunction(stype.data))
                    stype.data(serie);
            });

            return serie;
        };

        //  Draw the chart Serie
        serie.draw = function () {
            var opts = chart.options(),
                stype;

            //  Create the group
            if (!group) {

                // Remove previous serie drawing if any
                opts.chartTypes.forEach(function (type) {
                    stype = serie[type];
                    if (stype) {
                        if(isFunction(stype.options))
                            stype = stype.options();
                        serie[type] = stype;
                    }
                });

                group = chart.paper().group(groupOptions);

                // Is this the reference serie for its axisgroup?
                if (serie.reference)
                    group.element().classed('reference', true)
                                   .classed(chart.axisGroupId(serie.axisgroup), true);

                // Draw X axis or set the scale of the reference X-axis
                if (drawXaxis)
                    domain(group.xaxis(), 'x').xaxis().draw();
                else if (serie.axisgroup)
                    scale(group.xaxis());

                // Draw Y axis or set the scale of the reference Y-axis
                if (drawYaxis)
                    domain(group.yaxis(), 'y').yaxis().draw();
                else if (serie.axisgroup)
                    scale(group.yaxis());

                opts.chartTypes.forEach(function (type) {
                    stype = serie[type];
                    if (stype)
                        serie[type] = chartTypes[type](group, serie, stype)
                                                .x(serie.x())
                                                .y(serie.y())
                                                .label(serie.label());
                });
            } else {
                opts.chartTypes.forEach(function (type) {
                    stype = serie[type];
                    if (stype)
                        serie[type].label(serie.label);
                });
                drawXaxis ? domain(group.xaxis()) : scale(group.xaxis());
                drawYaxis ? domain(group.yaxis()) : scale(group.yaxis());
            }

            return serie;

            function domain(axis, xy) {
                var p = allranges[serie.axisgroup][axis.orient()],
                    o = axis.options(),
                    scale = axis.scale(),
                    opadding = 0.1;

                if (!p.range) scale = group.ordinalScale(axis);

                p.scale = scale;
                if (scale.rangeBand) {
                    scale.domain(data.map(function (d) {return d[xy];}));
                } else if (o.auto) {
                    scale.domain([p.range[0], p.range[1]]);
                    if (o.nice)
                        scale.nice();
                    if (!isNull(o.min))
                        scale.domain([o.min, scale.domain()[1]]);
                    else if (!isNull(o.max))
                        scale.domain([scale.domain()[0], o.max]);
                } else {
                    scale.domain([o.min, o.max]);
                }
                return group;
            }

            function scale (axis) {
                if (serie.axisgroup) {
                    var p = allranges[serie.axisgroup][axis.orient()];
                    if (p.scale)
                        axis.scale(p.scale);
                }
            }
        };

        function setRange (position, range) {
            var ranges = allranges[serie.axisgroup],
                p = ranges[position];

            // range is not available
            if (!p) {
                ranges[position] = {range: range};
                return true;
            } else if (p.range && range)
                p.range = [Math.min(p.range[0], range[0]),
                           Math.max(p.range[1], range[1])];
            return false;
        }
    }


    function scaled (c) {

        function f(group, data, opts) {
            return c(group, data, opts)
                        .x(function (d) {return d.x;})
                        .y(function (d) {return d.y;});
        }

        f.scaled = true;

        return f;
    }

    var chartTypes = {

        geo: function (group, data, opts) {
            return group.geo(data, opts);
        },

        pie: function (group, data, opts) {
            return group.pie(data, opts);
        },

        bar: scaled(function (group, data, opts) {
            return group.barchart(data, opts);
        }),

        line: scaled(function (group, data, opts) {
            return group.path(data, opts);
        }),

        point: scaled(function (group, data, opts) {
            return group.points(data, opts);
        }),

        custom: function (group, data, opts) {
            var draw = drawing(group, function () {
                    return opts.show.call(this);
                }).options(opts).data(data);

            if (group.type() === 'canvas') {
                draw = canvasMixin(draw);
                draw.each = function (callback) {
                    callback.call(draw);
                    return draw;
                };
            }

            return group.add(draw);
        }
    };

    //
    // Manage a collection of visualizations
    g.createviz('collection', {

            paper: false
        },

        function (collection) {

            var vizs = {};

            collection.set = function (key, viz) {
                vizs[key] = viz;
            };

            collection.size = function () {
                return size(vizs);
            };

            // Required by the visualization class
            collection.resume = function () {

                var opts = collection.options();

                forEach(vizs, function (viz, key) {
                    var o = opts[key];
                    if (o) viz.options(o);
                    viz.data(collection.data()).start();
                });
            };
        });

    g.createviz('map', {
        tile: null,
        center: [41.898582, 12.476801],
        zoom: 4,
        maxZoom: 18,
        zoomControl: true,
        wheelZoom: true,
    }, function (viz) {

        viz.start = function () {};

        viz.innerMap = function () {};

        viz.addLayer = function (collection, draw) {};

        // Override when tile provider available
        if (opts.tile)
            g.viz.map.tileProviders[opts.tile](viz, opts);

    }).tileProviders = {};

    //
    //  Leaflet tiles
    g.viz.map.tileProviders.leaflet = function (viz, opts) {
        var map,
            callbacks = [];

        // Override start
        viz.start = function () {
            if (typeof L === 'undefined') {
                g._.loadCss(g.constants.leaflet);
                g.require(['leaflet'], function () {
                    viz.start();
                });
            } else {
                map = new L.map(viz.element().node(), {
                    center: opts.center,
                    zoom: opts.zoom
                });
                if (opts.zoomControl) {
                    if (!opts.wheelZoom)
                        map.scrollWheelZoom.disable();
                } else {
                    map.dragging.disable();
                    map.touchZoom.disable();
                    map.doubleClickZoom.disable();
                    map.scrollWheelZoom.disable();

                    // Disable tap handler, if present.
                    if (map.tap) map.tap.disable();
                }

                // Attach the view reset callback
                map.on("viewreset", function () {
                    for (var i=0; i<callbacks.length; ++i)
                        callbacks[i]();
                });

                viz.resume();
            }
        };

        viz.innerMap = function () {
            return map;
        };

        viz.addLayer = function (url, options) {
            if (map)
                L.tileLayer(url, options).addTo(map);
        };

        viz.addOverlay = function (collection, callback) {
            var transform = d3.geo.transform({point: ProjectPoint}),
                path = d3.geo.path().projection(transform),
                svg = map ? d3.select(map.getPanes().overlayPane).append("svg") : null,
                g = svg ? svg.append("g").attr("class", "leaflet-zoom-hide") : null,
                draw = function () {
                    var bounds = path.bounds(collection),
                        topLeft = bounds[0],
                        bottomRight = bounds[1];

                    svg.attr("width", bottomRight[0] - topLeft[0])
                        .attr("height", bottomRight[1] - topLeft[1])
                        .style("left", topLeft[0] + "px")
                        .style("top", topLeft[1] + "px");

                    g.attr("transform", "translate(" + -topLeft[0] + "," + -topLeft[1] + ")");

                    if (callback)
                        callback(path);
                };

            callbacks.push(draw);

            return {
                element: g,
                collection: collection,
                path: path,
                draw: draw
            };
        };

        // Use Leaflet to implement a D3 geometric transformation.
        function ProjectPoint (x, y) {
            var point = map.latLngToLayerPoint(new L.LatLng(y, x));
            this.stream.point(point.x, point.y);
        }

    };




    g.slider = function () {
        // Public variables width default settings
        var min = 0,
            max = 100,
            step = 0.01,
            animate = true,
            orientation = "horizontal",
            axis = false,
            margin = 50,
            active = 1,
            snap = false,
            theme = 'default',
            value,
            scale;

        // Private variables
        var axisScale,
            dispatch = d3.dispatch("slide", "slideend"),
            formatPercent = d3.format(".2%"),
            tickFormat = d3.format(".0"),
            handle1,
            handle2 = null,
            sliderLength;

        function slider (selection) {

            selection.each(function() {
                var uid = ++_idCounter;

                // Create scale if not defined by user
                if (!scale) scale = d3.scale.linear().domain([min, max]);

                // Start value
                value = value || scale.domain()[0];

                // DIV container
                var div = d3.select(this).classed("d3-slider d3-slider-" + orientation + " d3-slider-" + theme, true);

                var drag = d3.behavior.drag();
                drag.on('dragend', function() {
                    dispatch.slideend(d3.event, value);
                });

                // Slider handle
                //if range slider, create two
                var divRange;

                if (value.length == 2) {
                    handle1 = div.append("a")
                        .classed("d3-slider-handle", true)
                        .attr("xlink:href", "#")
                        .attr('id', "handle-one")
                        .on("click", stopPropagation)
                        .call(drag);
                    handle2 = div.append("a")
                        .classed("d3-slider-handle", true)
                        .attr('id', "handle-two")
                        .attr("xlink:href", "#")
                        .on("click", stopPropagation)
                        .call(drag);
                } else {
                    handle1 = div.append("a")
                        .classed("d3-slider-handle", true)
                        .attr("xlink:href", "#")
                        .attr('id', "handle-one")
                        .on("click", stopPropagation)
                        .call(drag);
                }

                // Horizontal slider
                if (orientation === "horizontal") {

                    div.on("click", onClickHorizontal);

                    if (value.length == 2) {
                        divRange = d3.select(this).append('div').classed("d3-slider-range", true);

                        handle1.style("left", formatPercent(scale(value[0])));
                        divRange.style("left", formatPercent(scale(value[0])));
                        drag.on("drag", onDragHorizontal);

                        var width = 100 - parseFloat(formatPercent(scale(value[1])));
                        handle2.style("left", formatPercent(scale(value[1])));
                        divRange.style("right", width + "%");
                        drag.on("drag", onDragHorizontal);

                    } else {
                        handle1.style("left", formatPercent(scale(value)));
                        drag.on("drag", onDragHorizontal);
                    }

                    sliderLength = parseInt(div.style("width"), 10);

                } else { // Vertical

                    div.on("click", onClickVertical);
                    drag.on("drag", onDragVertical);
                    if (value.length == 2) {
                        divRange = d3.select(this).append('div').classed("d3-slider-range-vertical", true);

                        handle1.style("bottom", formatPercent(scale(value[0])));
                        divRange.style("bottom", formatPercent(scale(value[0])));
                        drag.on("drag", onDragVertical);

                        var top = 100 - parseFloat(formatPercent(scale(value[1])));
                        handle2.style("bottom", formatPercent(scale(value[1])));
                        divRange.style("top", top + "%");
                        drag.on("drag", onDragVertical);

                    } else {
                        handle1.style("bottom", formatPercent(scale(value)));
                        drag.on("drag", onDragVertical);
                    }

                    sliderLength = parseInt(div.style("height"), 10);

                }

                if (axis) {
                    var svg = createAxis();
                    renderAxis(svg);
                    d3.select(window).on('resize.slider' + uid, function () {
                        renderAxis();
                    });
                }


                function createAxis() {

                    // Create axis if not defined by user
                    if (typeof axis === "boolean") {

                        axis = d3.svg.axis()
                            .ticks(Math.round(sliderLength / 100))
                            .tickFormat(tickFormat)
                            .orient((orientation === "horizontal") ? "bottom" : "right");
                        div.classed('d3-slider-axis', true);

                    }

                    // Copy slider scale to move from percentages to pixels
                    axisScale = scale.copy().range([0, sliderLength]);
                    axis.scale(axisScale);

                    // Create SVG axis container
                    var s = div.append("svg")
                        .classed("d3-slider-axis d3-slider-axis-" + axis.orient(), true)
                        .on("click", stopPropagation);
                    s.append('g');
                    return s;
                }

                function renderAxis() {
                    var g = svg.select('g');

                    // Horizontal axis
                    if (orientation === "horizontal") {

                        svg.style("margin-left", - margin + "px");

                        svg.attr({
                            width: sliderLength + margin * 2,
                            height: margin
                        });

                        if (axis.orient() === "top") {
                            svg.style("top", - margin + "px");
                            g.attr("transform", "translate(" + margin + "," + margin + ")");
                        } else { // bottom
                            g.attr("transform", "translate(" + margin + ",0)");
                        }

                    } else { // Vertical

                        svg.style("top", - margin + "px");

                        svg.attr({
                            width: margin,
                            height: sliderLength + margin * 2
                        });

                        if (axis.orient() === "left") {
                            svg.style("left", - margin + "px");
                            g.attr("transform", "translate(" + margin + "," + margin + ")");
                        } else { // right
                            g.attr("transform", "translate(" + 0 + "," + margin + ")");
                        }

                    }

                    g.call(axis);
                }

                function onClickHorizontal() {
                    if (!value.length) {
                        var pos = Math.max(0, Math.min(sliderLength, d3.event.offsetX || d3.event.layerX));
                        moveHandle(stepValue(scale.invert(pos / sliderLength)));
                    }
                }

                function onClickVertical() {
                    if (!value.length) {
                        var pos = sliderLength - Math.max(0, Math.min(sliderLength, d3.event.offsetY || d3.event.layerY));
                        moveHandle(stepValue(scale.invert(pos / sliderLength)));
                    }
                }

                function onDragHorizontal() {
                    if (d3.event.sourceEvent.target.id === "handle-one") {
                        active = 1;
                    } else if (d3.event.sourceEvent.target.id == "handle-two") {
                        active = 2;
                    }
                    var pos = Math.max(0, Math.min(sliderLength, d3.event.x));
                    moveHandle(stepValue(scale.invert(pos / sliderLength)));
                }

                function onDragVertical() {
                    if (d3.event.sourceEvent.target.id === "handle-one") {
                        active = 1;
                    } else if (d3.event.sourceEvent.target.id == "handle-two") {
                        active = 2;
                    }
                    var pos = sliderLength - Math.max(0, Math.min(sliderLength, d3.event.y));
                    moveHandle(stepValue(scale.invert(pos / sliderLength)));
                }

                function stopPropagation() {
                    d3.event.stopPropagation();
                }

            });

        }

        // Move slider handle on click/drag
        function moveHandle (newValue) {
            var currentValue = value.length ? value[active - 1] : value,
                oldPos = formatPercent(scale(stepValue(currentValue))),
                newPos = formatPercent(scale(stepValue(newValue))),
                position = (orientation === "horizontal") ? "left" : "bottom";
            if (oldPos !== newPos) {

                if (value.length === 2) {
                    value[active - 1] = newValue;
                    if (d3.event)
                        dispatch.slide(d3.event, value);
                } else if (d3.event)
                    dispatch.slide(d3.event.sourceEvent || d3.event, value = newValue);

                if (value[0] >= value[1]) return;
                if (active === 1) {
                    if (value.length === 2) {
                        (position === "left") ? divRange.style("left", newPos) : divRange.style("bottom", newPos);
                    }

                    if (animate) {
                        handle1.transition()
                            .styleTween(position, function() {
                            return d3.interpolate(oldPos, newPos);
                        })
                            .duration((typeof animate === "number") ? animate : 250);
                    } else {
                        handle1.style(position, newPos);
                    }
                } else {

                    var width = 100 - parseFloat(newPos);
                    var top = 100 - parseFloat(newPos);

                    (position === "left") ? divRange.style("right", width + "%") : divRange.style("top", top + "%");

                    if (animate) {
                        handle2.transition()
                            .styleTween(position, function() {
                            return d3.interpolate(oldPos, newPos);
                        })
                            .duration((typeof animate === "number") ? animate : 250);
                    } else {
                        handle2.style(position, newPos);
                    }
                }
            }
        }

        // Calculate nearest step value
        function stepValue (val) {

            if (val === scale.domain()[0] || val === scale.domain()[1]) {
                return val;
            }

            var alignValue = val;
            if (snap) {
                var val_i = scale(val);
                var dist = scale.ticks().map(function(d) {
                    return val_i - scale(d);
                });
                var i = -1,
                    index = 0,
                    r = scale.range()[1];
                do {
                    i++;
                    if (Math.abs(dist[i]) < r) {
                        r = Math.abs(dist[i]);
                        index = i;
                    }
                } while (dist[i] > 0 && i < dist.length - 1);
                alignValue = scale.ticks()[index];
            } else {
                var valModStep = (val - scale.domain()[0]) % step;
                alignValue = val - valModStep;

                if (Math.abs(valModStep) * 2 >= step) {
                    alignValue += (valModStep > 0) ? step : -step;
                }
            }

            return alignValue;

        }

        // Getter/setter functions
        slider.min = function(_) {
            if (!arguments.length) return min;
            min = _;
            return slider;
        };

        slider.max = function(_) {
            if (!arguments.length) return max;
            max = _;
            return slider;
        };

        slider.step = function(_) {
            if (!arguments.length) return step;
            step = _;
            return slider;
        };

        slider.animate = function(_) {
            if (!arguments.length) return animate;
            animate = _;
            return slider;
        };

        slider.orientation = function(_) {
            if (!arguments.length) return orientation;
            orientation = _;
            return slider;
        };

        slider.axis = function(_) {
            if (!arguments.length) return axis;
            axis = _;
            return slider;
        };

        slider.value = function(_) {
            if (!arguments.length) return value;
            if (value)
                moveHandle(stepValue(_));
            value = _;
            return slider;
        };

        slider.snap = function(_) {
            if (!arguments.length) return snap;
            snap = _;
            return slider;
        };

        slider.scale = function(_) {
            if (!arguments.length) return scale;
            scale = _;
            return slider;
        };

        d3.rebind(slider, dispatch, "on");

        return slider;
    };

    g.viz.slider = function (element) {
        var slider = giottoMixin(g.slider()),
            options = slider.options;

        slider.options = function (_) {
            if (!arguments.length) return options();
            forEach(_, function (value, key) {
                if (isFunction(slider[key])) slider[key](value);
            });
            return options(_);
        };

        slider.start = function () {
            slider(d3.select(element));
            var opts = options(),
                onInit = opts.onInit;
            if (onInit) onInit(slider, opts);
        };

        slider.data = function () {
            return slider;
        };

        return slider;
    };
    g.viz.slider.vizName = function () {
        return 'slider';
    };

    //
    //  Sunburst visualization
    //
    g.createviz('sunburst', {
        // Show labels
        labels: true,
        // Add the order of labels if available in the data
        addorder: false,
        // speed in transitions
        transition: {
            duration: 750
        },
        //
        scale: 'sqrt',
        //
        initNode: null
    },

    function (self) {

        var namecolors = {},
            current,
            paper,
            group,
            textSize,
            radius,
            textContainer,
            dummyPath,
            text,
            positions,
            path, x, y, arc;


        self.on('tick.main', function (e) {
            self.stop();
            self.draw();
        });

        // API
        //
        // Select a path
        self.select = function (node, transition) {
            if (!current) return;

            if (isArray(node)) {
                var path = node;
                node = self.root();
                for (var n=0; n<path.length; ++n) {
                    var name = path[n];
                    if (node.children) {
                        for (var i=0; i<=node.children.length; ++i) {
                            if (node.children[i] && node.children[i].name === name) {
                                node = node.children[i];
                                break;
                            }
                        }
                    } else {
                        break;
                    }
                }
            }
            return select(node, transition);
        };

        // Return the current selected node
        self.current = function () {
            return current;
        };

        // Return the root node
        self.root = function () {
            var r = current;
            while (r && r.parent)
                r = r.parent;
            return r;
        };

        // Set the scale or returns it
        self.scale = function (scale) {
            var opts = self.options();
            if (!arguments.length) return opts.scale;
            opts.scale = scale;
            return self;
        };

        // draw
        self.draw = function () {
            var data = self.data(),
                opts = self.options();

            if (!paper || opts.type !== group.type()) {
                paper = self.paper(true);
                group = paper.group();
                group.element().classed('sunburst', true);
            }

            if (data) {
                data = d3.layout.partition()
                    .value(function(d) { return d.size; })
                    .sort(function (d) { return d.order === undefined ? d.size : d.order;})
                    .nodes(data);
                current = (isFunction(opts.initNode) ? opts.initNode() : opts.initNode) || data[0];

                group.add(function () {
                    build(data, current);
                });
            }

            self.render();
        };

        // Private methods
        //
        function build (data, initNode) {

            var width = 0.5*group.innerWidth(),
                height = 0.5*group.innerHeight(),
                xs = group.marginLeft() + width,
                ys = group.marginTop() + height,
                opts = self.options(),
                sunburst = group.element().attr("transform", "translate(" + xs + "," + ys + ")");

            current = data[0];
            radius = Math.min(width, height);
            textSize = calcTextSize();
            x = d3.scale.linear().range([0, 2 * Math.PI]);  // angular position
            y = scale(radius);  // radial position
            arc = d3[group.type()].arc()
                    .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x))); })
                    .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x + d.dx))); })
                    .innerRadius(function(d) { return Math.max(0, y(d.y)); })
                    .outerRadius(function(d) { return Math.max(0, y(d.y + d.dy)); });

            sunburst.selectAll('*').remove();

            path = sunburst.selectAll("path")
                    .data(data)
                    .enter()
                    .append('path')
                    .attr("d", arc)
                    .style("fill", function(d) {
                        var name = (d.children ? d : d.parent).name;
                        if (!namecolors[name])
                            namecolors[name] = group.pickColor();
                        return namecolors[name];
                    });

            if (opts.labels) {
                positions = [];
                textContainer = sunburst.append('g')
                                .attr('class', 'text')
                                .selectAll('g')
                                .data(path.data())
                                .enter().append('g');
                dummyPath = textContainer.append('path')
                        .attr("d", arc)
                        .attr("opacity", 0)
                        .on("click", function (d) {select(d);});
                text = textContainer.append('text')
                        .text(function(d) {
                            if (opts.addorder !== undefined && d.order !== undefined)
                                return d.order + ' - ' + d.name;
                            else
                                return d.name;
                        });
                alignText(text);
            }

            //
            if (!self.select(initNode, 0))
                self.event('change').call(self, {type: 'change'});
        }

        function scale (radius) {
            var opts = self.options();
            //if (opts.scale === 'log')
            //    return d3.scale.log().range([1, radius]);
            if (opts.scale === 'linear')
                return d3.scale.linear().range([0, radius]);
            else
                return d3.scale.sqrt().range([0, radius]);
        }

        // Calculate the text size to use from dimensions
        function calcTextSize () {
            var dim = Math.min(group.innerWidth(), group.innerHeight());
            if (dim < 400)
                return Math.round(100 - 0.15*(500-dim));
            else
                return 100;
        }

        function select (node, transition) {
            if (!node || node === current) return;
            var opts = self.options();

            if (transition === undefined) transition = +opts.transition.duration;

            if (text) text.transition().attr("opacity", 0);
            //
            function visible (e) {
                return e.x >= node.x && e.x < (node.x + node.dx);
            }

            var arct = arcTween(node);

            path.transition()
                .duration(transition)
                .attrTween("d", arct)
                .each('end', function (e, i) {
                    if (node === e) {
                        current = e;
                        self.event('change').call(self, {type: 'change'});
                    }
                });

            if (text) {
                positions = [];
                dummyPath.transition()
                    .duration(transition)
                    .attrTween("d", arct)
                    .each('end', function (e, i) {
                        // check if the animated element's data lies within the visible angle span given in d
                        if (e.depth >= current.depth && visible(e)) {
                            // fade in the text element and recalculate positions
                            alignText(d3.select(this.parentNode)
                                        .select("text")
                                        .transition().duration(transition)
                                        .attr("opacity", 1));
                        }
                    });
            }
            return true;
        }

        function calculateAngle (d) {
            var a = x(d.x + d.dx / 2),
                changed = true,
                tole=Math.PI/40;

            function tween (angle) {
                var da = a - angle;
                if (da >= 0 && da < tole) {
                    a += tole;
                    changed = true;
                }
                else if (da < 0 && da > -tole) {
                    a -= tole - da;
                    changed = true;
                }
            }

            while (changed) {
                changed = false;
                positions.forEach(tween);
            }
            positions.push(a);
            return a;
        }

        // Align text when labels are displaid
        function alignText (text) {
            var depth = current.depth,
                a;
            return text.attr("x", function(d, i) {
                // Set the Radial position
                if (d.depth === depth)
                    return 0;
                else {
                    a = calculateAngle(d, x, y);
                    this.__data__.angle = a;
                    return a > Math.PI ? -y(d.y) : y(d.y);
                }
            }).attr("dx", function(d) {
                // Set the margin
                return d.depth === depth ? 0 : (d.angle > Math.PI ? -6 : 6);
            }).attr("dy", function(d) {
                // Set the Radial position
                if (d.depth === depth)
                    return d.depth ? 40 : 0;
                else
                    return ".35em";
            }).attr("transform", function(d) {
                // Set the Angular position
                a = 0;
                if (d.depth > depth) {
                    a = d.angle;
                    if (a > Math.PI)
                        a -= Math.PI;
                    a -= Math.PI / 2;
                }
                return "rotate(" + (a / Math.PI * 180) + ")";
            }).attr("text-anchor", function (d) {
                // Make sure text is never oriented downwards
                a = d.angle;
                if (d.depth === depth)
                    return "middle";
                else if (a && a > Math.PI)
                    return "end";
                else
                    return "start";
            }).style("font-size", function(d) {
                var g = d.depth - depth,
                    pc = textSize;
                if (!g) pc *= 1.2;
                else if (g > 0)
                    pc = Math.max((1.2*pc - 20*g), 30);
                return Math.round(pc) + '%';
            });
        }

        // Interpolate the scales!
        function arcTween(d) {
            var xd = d3.interpolate(x.domain(), [d.x, d.x + d.dx]),
                yd = d3.interpolate(y.domain(), [d.y, 1]),
                yr = d3.interpolate(y.range(), [d.y ? 20 : 0, radius]);
            return function(d, i) {
                return i ? function(t) {
                    return arc(d);
                } : function(t) {
                    x.domain(xd(t));
                    y.domain(yd(t)).range(yr(t));
                    return arc(d);
                };
            };
        }
    });

    //
    //  Trianglify visualization
    //  ===========================
    //
    //  Requires trianglify library loaded or an entry ``trianglify`` in your
    //  require config.
    g.createviz('trianglify', {
        fillOpacity: 1,
        strokeOpacity: 1,
        variance: 0.75,
        seed: null,
        cell_size: 80,
        color: null,
        x_color: null,
        y_color: null
    }, function (tri) {

        var t;

        tri.gradient = function (value) {
            if (value && typeof(value) === 'string') {
                var bits = value.split('-');
                if (bits.length === 2) {
                    var palette = Trianglify.colorbrewer[bits[0]],
                        num = +bits[1];
                    if (palette) {
                        return palette[num];
                    }
                }
            }
        };
        //
        tri.on('tick.main', function (e) {
            // Load data if not already available
            tri.stop();
            if (tri.Trianglify === undefined && typeof Trianglify === 'undefined') {
                require(['trianglify'], function (Trianglify) {
                    tri.Trianglify = Trianglify || null;
                    tri.resume();
                });
            } else {
                if (tri.Trianglify === undefined)
                    tri.Trianglify = Trianglify;
                build();
            }
        });


        function build () {
            var opts = tri.options(),
                cell_size = +opts.cell_size,
                color = tri.gradient(opts.color),
                x_color = tri.gradient(opts.x_gradient) || color,
                y_color = tri.gradient(opts.y_gradient) || color,
                paper = tri.paper(),
                element = paper.element(),
                size = paper.size();

            //element.selectAll('.trianglify-background').remove();
            if (!t) {
                paper.on('change.trianglify' + paper.uid(), build);
                //highjack paper.image()
                paper.image = function () {
                    var url = pattern.dataUrl;
                    return url.substring(4,url.length-1);
                };
            }

            var topts = t.opts;
            if (x_color)
                topts.x_color = x_color;
            if (y_gradient)
                topts.y_color = y_color;
            if (cell_size > 0) {
                topts.cell_size = cell_size;
            }
            var pattern = tri.Trianglify(topts),
                telement = element.select('.trianglify-background');
            if (!telement.node()) {
                var parentNode = element.node(),
                    node = document.createElement('div'),
                    inner = parentNode.childNodes;
                while (inner.length) {
                    node.appendChild(inner[0]);
                }
                node.className = 'trianglify-background';
                parentNode.appendChild(node);
                telement = element.select('.trianglify-background');
            }
            telement.style("min-height", "100%")
                   //.style("height", this.attrs.height+"px")
                   //.style("width", this.attrs.width+"px")
                    .style("background-image", pattern.dataUrl);
        }
    });


    // Axis functionalities for groups
    g.themes.light.axis = {
        color: '#888',
        colorOpacity: 1
    };
    g.themes.dark.axis = {
        color: '#888',
        colorOpacity: 1
    };

    g.paper.plugin('axis', {

        defaults: {
            show: false,
            tickSize: '6px',
            outerTickSize: '6px',
            tickPadding: '3px',
            lineWidth: 1,
            textRotate: 0,
            textAnchor: null,
            color: ctheme.axis.color,
            colorOpacity: ctheme.axis.colorOpacity,
            //minTickSize: undefined,
            min: null,
            max: null,
            //  axis scale
            //  can be a function or a string such as 'linear', 'log', 'time'
            scale: 'linear',
            font: {
                color: ctheme.axis.color
            }
        },

        init: function (group) {
            var type = group.type(),
                d3v = d3[type],
                xaxis = d3v.axis(),
                yaxis = d3v.axis();

            [xaxis, yaxis].forEach(function (axis, i) {
                var d = i === 0 ? 'x' : 'y',
                    name = d + 'axis';

                axis.options = function () {
                    return group.options()[name];
                };

                group[name] = function () {
                    return axis;
                };

                axis.draw = function () {
                    return group.add(g[type].axis(group, axis, d + '-axis')).options(axis.options());
                };

                group['scale'+d] = function (v) {
                    return axis.scale()(v);
                };

                // coordinate in the input domain
                group[d] = function (u) {
                    var d = axis.scale().domain();
                    return u*(d[d.length-1] - d[0]) + d[0];
                };
            });

            group.ordinalScale = function (axis, range) {
                var scale = axis.scale(),
                    o = axis.options();
                o.auto = false,
                o.scale = 'ordinal';
                if (!scale.rangeBand) {
                    range = range || scale.range();
                    scale = axis.scale(d3.scale.ordinal()).scale();
                } else
                    range = range || scale.rangeExtent();
                return scale.rangeRoundBands(range, 0.2);
            };

            group.resetAxis = function () {
                var ranges = [[0, group.innerWidth()], [group.innerHeight(), 0]];
                group.scale().range(ranges[0]);

                [xaxis, yaxis].forEach(function (axis, i) {
                    var o = axis.options(),
                        scale;

                    if (o.scale === 'ordinal') {
                        axis.scale(group.ordinalScale(axis, ranges[i]));
                    } else {
                        o.auto = isNull(o.min) || isNull(o.max);
                        if (isFunction(o.scale))
                            axis.scale(o.scale);
                        else if (o.scale === 'time')
                            axis.scale(d3.time.scale());
                        else if (isString(o.scale)) {
                            var dn = d3.scale[o.scale];
                            if (isFunction(dn))
                                axis.scale(dn());
                        }
                        scale = axis.scale();
                        scale.range(ranges[i]);
                    }

                    var innerTickSize = group.scale(group.dim(o.tickSize)),
                        outerTickSize = group.scale(group.dim(o.outerTickSize)),
                        tickPadding = group.scale(group.dim(o.tickPadding));
                    axis.tickSize(innerTickSize, outerTickSize)
                          .tickPadding(tickPadding)
                          .orient(o.position);

                    //if (!o.tickFormat && o.scale === 'time') o.tickFormat = '%Y-%m-%d';

                    if (o.tickFormat) {
                        var f = o.tickFormat;
                        if (isString(f)) {
                            if (o.scale === 'time') f = d3.time.format(f);
                            else f = d3.format(f);
                        }
                        axis.tickFormat(f);
                    }
                });
                return group;
            };

            group.resetAxis();
        },

        extend: function (opts, value) {
            //
            // Create three new plugins
            var axis = opts.axis,
                o = registerPlugin({});

            o.plugin('xaxis', {
                deep: ['font'],
                defaults: extend({position: 'bottom'}, opts.axis, value)
            });
            o.plugin('yaxis', {
                deep: ['font'],
                defaults: extend({position: 'left', nice: true}, opts.axis, value)
            });
            o.plugin('yaxis2', {
                deep: ['font'],
                defaults: extend({position: 'right', nice: true}, opts.axis, value)
            });

            opts.pluginOptions(o.pluginArray);
        }
    });


    g.svg.axis = function (group, axis, xy) {
        return drawing(group, function () {
            var x =0,
                y = 0,
                ax = group.element().select('.' + xy),
                opts = this.options(),
                font = opts.font;
            if (opts.show === false) {
                ax.remove();
                return;
            }
            if (!ax.node())
                ax = this.group().element().append('g').attr('class', xy);
            if (xy[0] === 'x')
                y = opts.position === 'top' ? 0 : this.group().innerHeight();
            else
                x = opts.position === 'left' ? 0 : this.group().innerWidth();
            //ax.selectAll('*').remove();
            ax.attr("transform", "translate(" + x + "," + y + ")").call(axis);
            ax.selectAll('line, path')
                 .attr('stroke', this.color)
                 .attr('stroke-opacity', this.colorOpacity)
                 .attr('stroke-width', this.lineWidth)
                 .attr('fill', 'none');
            if (!font)
                ax.selectAll('text').remove();
            else {
                var text = ax.selectAll('text');
                if (opts.textRotate)
                    text.attr('transform', 'rotate(' + opts.textRotate + ')');
                if (opts.textAnchor)
                    text.style('text-anchor', opts.textAnchor);
                if (opts.dx)
                    text.attr('dx', opts.dx);
                if (opts.dy)
                    text.attr('dy', opts.dy);
                svg_font(text, font);
            }
            return ax;
        });
    };


    g.canvas.axis = function (group, axis, xy) {
        var d = canvasMixin(drawing(group)),
            ctx;

        d.render = function () {
            var x = 0,
                y = 0,
                ctx = d.context(),
                opts = d.options(),
                font = opts.font;

            if (!opts.show) return d;

            ctx.save();
            group.transform(ctx);

            // size of font
            if (font) {
                var size = font.size;
                font.size = group.scale(group.dim(size)) + 'px';
                ctx.font = fontString(font);
                font.size = size;
            }

            ctx.strokeStyle = d3.canvas.rgba(d.color, d.colorOpacity);
            ctx.fillStyle = d.color;
            ctx.lineWidth = group.factor()*d.lineWidth;

            if (xy[0] === 'x')
                y = opts.position === 'top' ? 0 : group.innerHeight();
            else
                x = opts.position === 'left' ? 0 : group.innerWidth();
            ctx.translate(x, y);
            axis.textRotate(d3_radians*(opts.textRotate || 0)).textAlign(opts.textAnchor);
            axis(d3.select(ctx.canvas));
            ctx.stroke();
            ctx.restore();
            return d;
        };

        return d;
    };

    //  Bar charts
    //  ==============
    //
    //  Bar charts to a group
    g.paper.plugin('bar', {
        deep: ['active', 'tooltip', 'transition'],

        defaults: {
            width: 'auto',
            color: null,
            fill: true,
            fillOpacity: 1,
            colorOpacity: 1,
            lineWidth: 1,
            // Radius in pixels of rounded corners. Set to 0 for no rounded corners
            radius: 4,
            active: {
                fill: 'darker',
                color: 'brighter'
            }
        },

        init: function (group) {
            var type = group.type();

            group.barchart = function (data, opts) {
                opts || (opts = {});
                chartFormats(group, opts);
                group.drawColor(copyMissing(group.options().bar, opts));

                return group.add(g[type].barchart)
                    .pointOptions(extendArray(['size'], drawingOptions))
                    .size(bar_size)
                    .options(opts)
                    .dataConstructor(bar_costructor)
                    .data(data);
            };
        }
    });


    var bar_costructor = function (rawdata) {
            var group = this.group(),
                draw = this,
                opts = this.options(),
                data = [],
                width = opts.width,
                bar = g[group.type()].bar;
            if (width === 'auto')
                width = function () {
                    return d3.round(0.8*(group.innerWidth() / draw.data().length));
                };

            rawdata.forEach(function (d) {
                data.push(bar(draw, d, width));
            });

            return data;
        },

        bar_size = function (d) {
            var w = d.size;
            if (typeof w === 'function') w = w();
            return w;
        };


    g.svg.bar = function (draw, data, size) {
        var d = drawingData(draw, data),
            group = draw.group();

        d.set('size', data.size === undefined ? size : data.size);
        d.render = function (element) {
            group.draw(element);
        };
        return d;
    };

    g.svg.barchart = function () {
        var group = this.group(),
            chart = group.element().select("#" + this.uid()),
            opts = this.options(),
            xscale = group.xaxis().scale(),
            scalex = this.scalex(),
            scaley = this.scaley(),
            size = this.size(),
            zero = group.scaley(0),
            data = this.data(),
            trans = opts.transition,
            bar, y;

        if (!chart.node())
            chart = group.element().append("g")
                        .attr('id', this.uid());

        bar = chart.selectAll(".bar").data(data);

        bar.enter()
            .append("rect")
            .attr('class', 'bar');

        bar.exit().remove();

        group.events(group.draw(bar));

        if (!group.resizing() && trans && trans.duration)
            bar = bar.transition().duration(trans.duration).ease(trans.ease);

        bar.attr("y", function(d) {
            return Math.min(zero, scaley(d.data));
        })
        .attr("height", function(d) {
            return abs(scaley(d.data) - zero);
        });

        // Ordinal scale
        if (xscale.rangeBand) {
            bar.attr("x", function(d) {
                return scalex(d.data);
            })
            .attr("width", xscale.rangeBand());

        } else {
            bar.attr("x", function(d) {
                return scalex(d.data) - 0.5*size(d);
            })
            .attr("width", size);
        }

        if (opts.radius > 0)
            bar.attr('rx', opts.radius).attr('ry', opts.radius);

        return chart;
    };

    g.canvas.barchart = function () {
        this.each(function () {
            this.reset().render();
        });
    };

    g.canvas.bar = function (draw, data, siz) {
        var d = canvasMixin(drawingData(draw, data)),
            group = d.group(),
            xscale = group.xaxis().scale(),
            scalex = draw.scalex(),
            scaley = draw.scaley(),
            size = draw.size(),
            factor = draw.factor(),
            x, y, y0, y1, w, w0, yb, radius;

        d.set('size', data.size === undefined ? siz : data.size);

        d.render = function () {
            return _draw(function (ctx) {
                d3.canvas.style(ctx, d);
                return d;
            });
        };

        d.inRange = function (ex, ey) {
            return _draw(function (ctx) {
                return ctx.isPointInPath(ex, ey);
            });
        };

        d.bbox = function () {
            var x = scalex(d.data) + group.marginLeft(),
                y1 = scaley(d.data) + group.marginTop(),
                y0 = group.scaley(0)  + group.marginTop(),
                yn = Math.min(y1, y0),
                ys = y1 + y0 - yn,
                w0 = 0,
                w;
            if (xscale.rangeBand)
                w = xscale.rangeBand();
            else
                w0 = w = 0.5*size(d);

            return canvasBBox(d, [x-w0, yn], [x+w, yn], [x+w, ys], [x-w0, ys]);
        };

        return d;

        function _draw (callback) {
            var ctx = d.context();
            ctx.save();
            group.transform(ctx);
            radius = factor*draw.options().radius;
            ctx.beginPath();
            x = scalex(d.data);
            w0 = 0;
            if (xscale.invert)
                w0 = w = 0.5*size(d);
            else
                w = xscale.rangeBand();
            y = scaley(d.data);
            y0 = group.scaley(0);
            d3.canvas.drawPolygon(ctx, [[x-w0, y0], [x+w, y0], [x+w, y], [x-w0, y]], radius);
            ctx.closePath();
            var r = callback(ctx);
            ctx.restore();
            return r;
        }
    };

    //
    //  Add brush functionality to svg paper
    g.paper.plugin('brush', {

        defaults: {
            axis: 'x', // set one of 'x', 'y' or 'xy'
            fill: '#000',
            fillOpacity: 0.125
        },

        init: function (group) {
            var brush, brushDrawing;

            group.brush = function () {
                return brush;
            };

            // Add a brush to the group if not already available
            group.addBrush = function (options) {
                if (brushDrawing) return brushDrawing;

                brushDrawing = group.add(function () {

                    var draw = this,
                        opts = draw.options(),
                        type = group.type(),
                        resizing = group.resizing();

                    if (!brush) {
                        resizing = true;
                        brush = d3[type].brush()
                                .on("brushstart", brushstart)
                                .on("brush", brushmove)
                                .on("brushend", brushend);

                        if (opts.axis === 'x' || opts.axis === 'xy')
                            brush.x(group.xaxis().scale());

                        if (opts.axis === 'y' || opts.axis === 'xy')
                            brush.y(group.yaxis().scale());

                        if (opts.extent) brush.extent(opts.extent);

                        if (type === 'svg') {
                            brush.selectDraw = selectDraw;

                        } else {

                            brush.selectDraw = function (draw) {
                                selectDraw(draw, group.paper().canvasOverlay().node().getContext('2d'));
                            };
                        }
                    }

                    if (resizing) {
                        brush.extent(brush.extent());

                        if (type === 'svg') {
                            var gb = group.element().select('.brush');

                            if (!gb.node())
                                gb = group.element().append('g').classed('brush', true);

                            var rect = gb.call(brush).selectAll("rect");

                            this.setBackground(rect);

                            if (opts.axis === 'x')
                                rect.attr("y", -6).attr("height", group.innerHeight() + 7);

                            brushstart();
                            brushmove();
                            brushend();
                        } else {
                            brush.fillStyle(d3.canvas.rgba(this.fill, this.fillOpacity))
                                 .rect([group.marginLeft(), group.marginTop(),
                                        group.innerWidth(), group.innerHeight()]);
                            group.paper().canvasOverlay().call(brush);
                        }
                    }

                    function brushstart () {
                        group.element().classed('selecting', true);
                        if (opts.start) opts.start();
                    }

                    function brushmove () {
                        if (opts.move) opts.move();
                    }

                    function brushend () {
                        group.element().classed('selecting', false);
                        if (opts.end) opts.end();
                    }

                });

                return brushDrawing.options(extend({}, group.options().brush, options));
            };

            function selectDraw (draw, ctx) {
                var x = draw.x(),
                    selected = [],
                    xval,
                    s = brush.extent();

                if (ctx) {
                    var group = draw.group();
                    ctx.save();
                    ctx.translate(group.marginLeft(), group.marginTop());
                }

                draw.each(function () {
                    if (this.data) {
                        xval = x(this.data);
                        if (s[0] <= xval && xval <= s[1]) {
                            this.highLight();
                            if (ctx) this.render(ctx);
                            selected.push(this);
                        }
                        else
                            this.reset();
                    }
                });

                if (ctx) ctx.restore();
                else draw.render();

                return selected;
            }
        }
    });

    //  Add brush functionality to charts
    g.viz.chart.plugin('brushchart', {

        init: function (chart) {
            var brush, brushopts;

            // Show grid
            chart.addBrush = function () {

                brush = chart.options().brush;

                var start = brush.start,
                    move = brush.move,
                    end = brush.end;

                brush.start = function () {
                    if (start) start(chart);
                };

                brush.move = function () {
                    //
                    // loop through series
                    chart.each(function (serie) {
                        var group = chart.axisGroup(serie),
                            brush = group ? group.brush() : null;

                        if (!brush) return;

                        if (serie.point)
                            brush.selectDraw(serie.point);
                        if (serie.bar)
                            brush.selectDraw(serie.bar);
                    });
                    if (move) move(chart);
                };

                brush.end = function () {
                    if (end) end(chart);
                };

                chart.paper().each('.reference', function () {
                    this.addBrush(brushopts).render();
                });
                return chart;
            };

            chart.on('tick.brush', function () {
                if (chart.options().brush.show)
                    chart.addBrush();
            });

        }
    });



    g.paper.plugin('bubble', {

        defaults: {
            force: false,
            theta: 0.8,
            friction: 0.9
        },

        init: function (group) {

            // Add force visualization to the group
            group.bubble = function (data, opts) {
                opts || (opts = {});
                chartFormats(group, opts);
                opts = copyMissing(group.options().bubble, opts);

                return group.add(g[type].bubble)
                            .dataConstructor(bubble_costructor)
                            .options(opts);
            };
        }
    });

    var bubble_costructor = function (rawdata) {
        return rawdata;
    };

    g.svg.bubble = function () {
        var group = this.group(),
            opts = this.options(),
            bubble = d3.layout.pack()
                        .padding(opts.padding)
                        .size([group.innerWidth(), group.innerHeight()])
                        .sort(null)
                        .data(this.data()),
            elem = group.element().selectAll("#" + this.uid()).data([true]);

        elem.enter().append('g').attr('id', thiss.uid());

    };
    //
    //  Colors
    //  ===========
    //
    //  Add margins to a giotto group
    //
    var fillSpecials = [true, 'none', 'color'],

        colorPlugin = {

            defaults: {
                scale: d3.scale.category10().range(),
                darkerColor: 0,
                brighterColor: 0,
                colorIndex: 0
            },

            init: function (self) {
                var opts = self.options().colors;

                // pick a color
                self.pickColor = function (index) {
                    if (arguments.length === 0)
                        index = opts.colorIndex++;
                    var dk = 0, bk = 0;
                    while (index >= opts.scale.length) {
                        index -= opts.scale.length;
                        dk += opts.darkerColor;
                        bk += opts.brighterColor;
                    }
                    var c = opts.scale[index];
                    if (dk)
                        c = d3.rgb(c).darker(dk).toString();
                    else if (bk)
                        c = d3.rgb(c).brighter(bk).toString();
                    return c;
                };

                //
                // Select a suitable color for a draw element
                self.drawColor = function (opts) {
                    if (!opts.color)
                        if (opts.fill && fillSpecials.indexOf(opts.fill) === -1)
                            opts.color = d3.rgb(opts.fill).darker().toString();
                        else
                            opts.color = self.pickColor();

                    if (opts.fill === true)
                        opts.fill = d3.rgb(opts.color).brighter().toString();
                    else if (opts.fill === 'color')
                        opts.fill = opts.color;

                    return opts.color;
                };
            },

            extend: function (opts, value) {
                opts.colors = extend({}, opts.colors, value);
                if (isFunction (opts.colors.scale)) opts.colors.scale = opts.colors.scale(d3);
            },

            clear: function (opts) {
                opts.colorIndex = 0;
            }
        };

    g.paper.plugin('colors', colorPlugin);
    g.viz.plugin('colors', colorPlugin);

    //
    //  Loading Data
    //  ===================
    //
    //  Load data into visualizations
    g.viz.plugin('data', {

        defaults: {
            //
            //  Data source, can be
            //  * Remote url
            //  * A data object/array
            //  * A function returning a url or data
            src: null,
            //
            //  Must be a function returning the data loader.
            //  The data loader is a function accepting a url and a callback
            loader: function (src) {
                var loader = d3.json;
                if (src.substring(src.length-4) === '.csv') loader = d3.csv;
                return loader;
            },
            //
            //  Optional function to pre-process data
            //
            //  This function accept data as the only parameter and the
            //  visualization is the caller. It should return a new data
            //  object.
            process: null
        },

        //
        //  Allow to specify a url instead of a data object
        extend: function (opts, value) {
            var name = this.name;
            opts[name] = extend({}, opts[name], isString(value) ? {src: value} : value);
        },

        init: function (viz) {

            var loading_data = false,
                data;

            //
            // Set/Get data for the visualization
            viz.data = function (inpdata, callback) {
                if (!arguments.length) return data;
                var opts = viz.options().data;

                if (opts.process)
                    inpdata = opts.process.call(viz, inpdata);

                data = inpdata;

                if (callback) callback();

                viz.fire('data');

                return viz;
            };

            //
            //  Load data for visualization
            viz.load = function (callback) {
                if (loading_data) return;

                var opts = viz.options().data,
                    src = opts.src;

                if (isFunction(src)) src = src();

                if (isString(src)) {

                    loading_data = true;
                    g.log.info('Giotto loading data from ' + src);
                    viz.fire('loadstart');

                    return opts.loader(src)(src, function(error, xd) {

                        loading_data = false;
                        viz.fire('loadend');

                        if (arguments.length === 1) xd = error;
                        else if(error)
                            return g.log.error(error);

                        g.log.info('Giotto got data from ' + src);
                        viz.data(xd, callback);
                    });

                } else if (src) {
                    delete opts.src;
                    viz.data(src, callback);

                } else if (callback) {
                    callback();
                }

                return viz;
            };
        }
    });

    //
    //  Fill plugin
    //  ================
    //
    //  A plugin which add the ``setBackground`` function to a group
    g.paper.plugin('fill', {

        init: function (group) {

            var type = group.type();

            group.fill = function (opts) {
                if (!isObject(opts)) opts = {fill: opts};

                return group.add(type === 'svg' ? FillSvg : FillCanvas)
                            .options(opts);
            };

            if (type === 'svg')
                group.setBackground = function (b, o) {
                    if (!o) return;

                    if (isObject(b)) {
                        if (b.fillOpacity !== undefined)
                            o.attr('fill-opacity', b.fillOpacity);
                        b = b.fill;
                    }
                    if (isString(b))
                        o.attr('fill', b);
                    else if(isFunction(b))
                        b(o);
                    return group;
                };
            else
                group.setBackground = function (b, context) {
                    var fill = b;
                    context = context || group.context();
                    if (isObject(fill)) fill = fill.fill;

                    if (isFunction(fill))
                        fill(group.element());
                    else if (isObject(b))
                        context.fillStyle = d3.canvas.rgba(b.fill, b.fillOpacity);
                    else if (isString(b))
                        context.fillStyle = b;
                    return group;
                };

            function FillSvg () {
                var rect = group.element().selectAll('rect').data([true]),
                    fill = this.fill;
                rect.enter().append('rect').attr('x', 0).attr('y', 0);
                rect.attr('width', group.innerWidth()).attr('height', group.innerWidth());
                group.setBackground(this, rect);
            }

            function FillCanvas () {
                var ctx = group.context(),
                    width = group.innerWidth(),
                    height = group.innerHeight();
                ctx.beginPath();
                ctx.rect(0, 0, width, height);
                if (isFunction(this.fill))
                    this.fill.x1(0).y1(0).x2(width).y2(height);
                group.setBackground(this);
            }
        }
    });

    //
    //  Geometric data handler
    //  ===========================
    //
    //  features, array of geometric features
    g.data.geo = function (features) {

        var value = function (d) {return d.value;},
            label = function (d) {return d.label;},
            minval=Infinity,
            maxval=-Infinity,
            scale = d3.scale.linear(),
            colors;

        function geo (serie, geodata, opts) {
            minval = Infinity;
            maxval = -Infinity;

            features.forEach(function (feature) {
                feature = {object: feature};
                d = serie.get(feature.object.id);
                if (d) {
                    val = +y(d);
                    if (val === val) {
                        minval = Math.min(val, minval);
                        maxval = Math.max(val, maxval);
                        feature.data = [label(d), val];
                        feature.fill = color(scale(val));
                    } else {
                        feature.active = false;
                        feature.fill = opts.missingFill;
                    }
                }
                data.push(feature);
            });
            if (scale(0) !== scale(0)) {
                minval = Math.max(minval, 1);
                maxval = Math.max(maxval, minval);
            }
            scale.domain([minval, maxval]);
            return data;
        }

        geo.value = function (_) {
            if (!arguments.length) return value;
            value = d3_functor(_);
            return geo;
        };

        geo.label = function (_) {
            if (!arguments.length) return label;
            label = d3_functor(_);
            return geo;
        };

        geo.data = function () {
            return data;
        };

        geo.minvalue = function () {
            return minval;
        };

        geo.maxvalue = function () {
            return maxval;
        };

        geo.scale = function (_) {
            if (!arguments.length) return scale;
            scale = _;
            return geo;
        };

        geo.colors = function (cols) {
            if (!arguments.length) return colors;
            colors = cols;
            return geo;
        };

        return geo;
    };

    //
    //  Geometry (Maps)
    //  =====================
    //
    //  Geo charts
    //
    g.paper.plugin('geo', {
        deep: ['active', 'tooltip', 'transition'],

        defaults: {
            scale: 1,
            color: '#333',
            missingFill: '#d9d9d9',
            fill: 'none',
            fillOpacity: 1,
            colorOpacity: 1,
            lineWidth: 0.5,
            projection: null,
            features: null,
            active: {
                fill: 'darker'
            },
            formatX: d3_identity,
            tooltip: {
                template: function (d) {
                    return "<p><strong>" + d.x + "</strong> " + d.y + "</p>";
                }
            }
        },

        init: function (group) {

            //
            //  Create a new drawing for geometric datasets
            group.geo = function (data, opts) {
                var type = group.type(),
                    features,
                    path;

                opts || (opts = {});
                copyMissing(group.options().geo, opts);
                group.element().classed('geo', true);

                return group.add(geodraw(group, g[type].geodraw))
                               .options(opts)
                               .data(data);
            };
        }
    });

    //
    //  geo drawing constructor
    //  Used by both SVG and Canvas geo renderer functions
    function geodraw (group, renderer) {
        var path = d3.geo.path(),
            feature = g[group.type()].feature,
            draw = drawing(group, renderer),
            dataFeatures,
            features;

        // Return the path constructor
        draw.path = function () {

            var opts = draw.options(),
                width = Math.round(0.5 * group.innerWidth()),
                height = Math.round(0.5 * group.innerHeight()),
                scale = Math.round(opts.scale*Math.min(width, height)),
                projection;

            if (opts.projection) {
                projection = opts.projection;
                if (isString(projection)) {
                    if (g.geo[projection]) {
                        g.geo[projection](draw, path);
                        return path;
                    }
                    projection = d3.geo[projection];
                }
            }
            if (!projection)
                projection = d3.geo.mercator;

            projection = projection()
                            .scale(scale)
                            .translate([width, height]);

            return path.projection(projection);
        };

        // Set get/geo topographic features
        draw.features = function (_) {
            if (!arguments.length) return features;
            features = _;
            dataFeatures = null;
            return draw;
        };

        draw.graticule = function () {
            var g = {object: d3.geo.graticule()()};
            return extend(g, group.options().grid, draw.options().grid);
        };

        draw.dataFeatures = function () {
            if (features && (draw.changed() || !dataFeatures))
                dataFeatures = buildDataFeatures();
            return dataFeatures;
        };

        return draw;

        function buildDataFeatures () {
            var geodata = [],
                opts = draw.options(),
                scale = group.yaxis().scale(),
                color = d3.scale.quantize().domain(scale.range()).range(opts.colors.scale);

            // Loop through features and pick data-geo functions
            features.forEach(function (geo) {
                if (isFunction(geo))
                    geo(draw);
                else {
                    geo.active = false;
                    geodata.push(feature(draw, null, geo));
                }
            });
            return geodata;
        }
    }

    // Draw the geo on SVG
    g.svg.geodraw = function () {
        var draw = this,
            opts = draw.options(),
            group = draw.group(),
            chart = group.element().selectAll("#" + draw.uid()),
            trans = opts.transition,
            features = draw.features(),
            resizing = group.resizing();

        if (!chart.size()) {
            chart = group.element().append("g").attr('id', draw.uid());
            resizing = true;
        }

        if (!features)
            return opts.features(function (features) {
                draw.features(features).render();
            });

        var geodata = draw.dataFeatures();
        if (opts.grid) {
            geodata = geodata.slice();
            geodata.push(draw.graticule());
        }

        var paths = chart.selectAll('path').data(geodata),
            path = draw.path();

        paths.enter().append('path');
        paths.exit().remove();
        group.events(paths);

        if (!resizing && trans && trans.duration)
            paths = paths.transition().duration(trans.duration).ease(trans.ease);

        group.draw(paths)
            .style('vector-effect', 'non-scaling-stroke')
            .attr('id', function (d) { return d.object.id;})
            .attr('d', function (d) {
                return path(d.object);
            });


        group.on('zoom.geo', function () {
            chart.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
        });
    };

    //  An svg feature in the geo
    //  Similar to a point in a point chart or a bar in a bar chart
    g.svg.feature = function (draw, data, feature) {
        var group = draw.group();
        feature = drawingData(draw, data, feature);

        feature.render = function (element) {
            group.draw(element);
        };

        return feature;
    };

    // Draw the geo on Canvas
    g.canvas.geodraw = function () {
        var draw = this,
            opts = draw.options(),
            group = draw.group(),
            features = draw.features();

        if (!features)
            return opts.features(function (features) {
                draw.features(features).render();
            });

        if (opts.grid) {
            features = features.slice();
            features.push(draw.graticule());
        }

        var path = draw.path(),
            ctx = group.context();

        path.context(ctx);
        features.forEach(function (d) {
            path(d.object);
        });
    };

    g.canvas.feature = function (draw, feature) {
        var group = draw.group();

        feature.render = function (element) {
            group.draw(element).attr('d', draw.symbol ? draw.symbol : draw.path());
        };

        return feature;
    };

    //
    //  Add grid functionality to a group
    //  =====================================
    //
    //  In theory each group can have its own grid
    g.themes.light.grid = {
        color: '#333',
        colorOpacity: 0.3
    };
    g.themes.dark.grid = {
        color: '#888',
        colorOpacity: 1
    };

    g.paper.plugin('grid', {

        defaults: {
            show: false,
            color: ctheme.grid.color,
            colorOpacity: ctheme.grid.colorOpacity,
            fill: 'none',
            fillOpacity: 0.2,
            lineWidth: 0.5,
            xaxis: true,
            yaxis: true
        },

        init: function (group) {
            var paper = group.paper(),
                grid, gopts;

            // Return the grid associated with the group
            // Can return nothing (no grid available)
            group.grid = function () {
                return grid;
            };

            // Show the grid
            group.showGrid = function () {
                if (!grid) {
                    // First time here, setup grid options for y and x coordinates
                    if (!gopts) {
                        var opts = group.options();
                        gopts = opts.copy({
                            xaxis: extend({
                                position: 'top',
                                size: 0,
                                show: opts.grid.xaxis
                            }, opts.grid),
                            yaxis: extend({
                                position: 'left',
                                size: 0,
                                show: opts.grid.yaxis
                            }, opts.grid)
                        });
                    }
                    // Create the grid group
                    gopts.before = '*';
                    grid = paper.group(gopts);
                    grid.element().classed('grid', true);
                    grid.xaxis().tickFormat(notick);
                    grid.yaxis().tickFormat(notick);
                    grid.add(Rectangle).options(gopts.grid);
                    if (gopts.xaxis.show) grid.xaxis().draw();
                    if (gopts.yaxis.show) grid.yaxis().draw();
                    grid.on('zoom', zoomgrid);
                    grid.render();
                } else
                    grid.clear().render();
                return group;
            };

            group.hideGrid = function () {
                if (grid)
                    grid.remove();
                return group;
            };

            // The redering function for the grid
            function Rectangle () {
                var width = grid.innerWidth(),
                    height = grid.innerHeight(),
                    type = grid.type(),
                    opts = this.group().options(),
                    scalex, scaley;

                if (type === 'svg') {
                    var rect = grid.element().select('.grid-rectangle');

                    if (!rect.node())
                        rect = grid.element()
                                    .append("rect")
                                    .attr("class", "grid-rectangle");

                    rect.attr("width", width).attr("height", height);
                    this.setBackground(rect);
                } else {
                    // canvas
                    var ctx = grid.context();
                    ctx.save();
                    group.transform(ctx);
                    ctx.beginPath();
                    ctx.rect(0, 0, width, height);
                    if (this.fill != 'none') {
                        this.setBackground(ctx);
                        ctx.fill();
                    }
                    ctx.restore();
                }

                grid.xaxis().scale(group.xaxis().scale()).tickSize(-height, 0);
                grid.yaxis().scale(group.xaxis().scale()).tickSize(-width, 0);
            }

            function zoomgrid () {
                if (scalex) {
                    var x1 = scalex.invert(opts.margin.left),
                        x2 = scalex.invert(opts.size[0] - opts.margin.right);
                    grid.xaxis().scale().domain([x1, x2]);
                }
                if (scaley) {
                    var y1 = scalex.invert(opts.margin.top),
                        y2 = scalex.invert(opts.size[1] - opts.margin.bottom);
                    grid.yaxis().scale().domain([y1, y2]);
                }
            }
        }
    });

    //
    //  Add grid functionality to charts
    g.viz.chart.plugin('gridchart', {

        init: function (chart) {

            // Show grid
            chart.showGrid = function () {
                chart.paper().each('.reference', function () {
                    this.showGrid();
                });
                return chart;
            };

            // Hide grid
            chart.hideGrid = function () {
                chart.paper().each('.reference', function () {
                    this.hideGrid();
                });
                return chart;
            };

            chart.on('tick.grid', function () {
                var grid = chart.options().grid;

                if (grid.show)
                    chart.showGrid();
                else
                    chart.hideGrid();
            });
        }
    });

    function notick () {return '';}


    var inlinePositions = ['bottom', 'top'];

    //
    //  Add legend functionality to Charts
    g.viz.chart.plugin('legend', {
        deep: ['font'],

        defaults: {
            show: false,
            draggable: true,
            margin: 50,
            position: 'top-right',
            padding: 5,
            textPadding: 5,
            fill: '#fff',
            fillOpacity: 1,
            color: '#000',
            colorOpacity: 1,
            lineWidth: 1,
            radius: 0,
            symbolLength: 30,
            symbolPadding: 10,
            font: {
                size: '14px'
            }
        },

        init: function (chart) {
            var opts;

            chart.Legend = function (build) {
                var labels = [],
                    group = chart.paper().select('.chart-legend');

                if (!group && build) {
                    group = chart.paper().classGroup('chart-legend', {margin: opts.legend.margin});
                    group.add(group.type() === 'svg' ? SvgLegend : CanvasLegend);
                }

                return group;
            };

            chart.on('tick.legend', function () {
                if (!opts) {
                    opts = chart.options();
                    opts.menu.items.push({
                        label: function () {
                            if (chart.paper().select('.chart-legend'))
                                return 'Hide legend';
                            else
                                return 'Show legend';
                        },
                        callback: function () {
                            var group = chart.paper().select('.chart-legend');
                            if (group) group.remove();
                            else chart.Legend(true).render();
                        }
                    });
                }

                if (chart.drawing()) return;
                if (opts.legend.show)
                    chart.Legend(true).render();
                else {
                    var legend = chart.Legend();
                    if (legend) legend.remove();
                }
            });

            function getLabels () {
                var labels = [];

                chart.each(function (serie) {
                    if (isArray(serie.legend))
                        serie.legend.forEach(function (label) {
                            addlabel(serie, label);
                        });
                    else
                        addlabel(serie, serie.legend);
                });

                return labels;

                function addlabel (serie, legend) {
                    legend || (legend = {});
                    if (!legend.label) legend.label = serie.label;
                    legend.line = serie.line;
                    legend.point = serie.point;
                    legend.bar = serie.bar;
                    legend.pie = serie.pie;
                    legend.index = labels.length;
                    labels.push(legend);
                }
            }

            function getPosition (group, width, height) {
                var position = opts.legend.position,
                    x, y;

                if (position.substring(0, 6) === 'bottom') {
                    position = position.substring(7);
                    y = group.height() - 1.7*height;
                } else if (position.substring(0, 3) === 'top') {
                    position = position.substring(4);
                    y = 0;
                } else
                    y = 0;

                if (position == 'left')
                    x = 0;
                else if (position === 'right')
                    x = 0.5*(group.innerWidth() - width);
                else
                    x = 0.5*(group.innerWidth() - width);

                return [x, y];
            }

            function SvgLegend () {
                var labels = getLabels(),
                    group = this.group(),
                    element = group.element()
                                    .selectAll('g.legend').data([true]),
                    box = group.element().selectAll('.legend-box').data([true]),
                    d = opts.legend,
                    padding = d.padding,
                    position = d.position,
                    inline = inlinePositions.indexOf(position) > -1,
                    fsize = group.scale(group.dim(d.font.size)),
                    lp = Math.round(fsize/3),
                    dy = fsize + d.textPadding,
                    dx = d.symbolLength + d.symbolPadding,
                    lineData = [[[0, 0], [d.symbolLength, 0]]],
                    line = d3.svg.line(),
                    symbol = d3.svg.symbol(),
                    drag = d3.behavior.drag()
                                .on("drag", dragMove)
                                .on('dragstart', dragStart),
                    x = 0,
                    y = 0,
                    t;

                function dragStart(d) {
                    d3.select('.legend-box').attr('cursor', 'move');
                    d3.select('.legend').attr('cursor', 'move');
                }

                function dragMove(d) {
                    var x = d3.event.x - 3*opts.legend.symbolLength,
                        y = d3.event.y;

                    d3.select('.legend-box').attr("transform", "translate(" + x + "," + y + ")");
                    d3.select('.legend').attr("transform", "translate(" + x + "," + y + ")");
                }

                box.enter().append('rect').classed('legend-box', true);
                element.enter().append('g').classed('legend', true);

                if (d.draggable) {
                    box.call(drag);
                    element.call(drag);
                }

                var items = element.selectAll('.legend-item').data(labels),
                    node = element.node();

                items.enter().append('g').classed('legend-item', true);
                items.exit().remove();

                items.each(function() {
                    var target = d3.select(this),
                        d = target.datum();
                    if (!inline) y = d.index*dy;

                    if (d.line && !d.bar) {
                        t = target.selectAll('path.line').data([true]);
                        t.enter().append('path').classed('line', true);
                        t.data(lineData)
                            .attr('transform', "translate(" + x + "," + (y-lp) + ")")
                            .attr('d', line)
                            .attr('stroke-width', d.lineWidth || d.line.lineWidth)
                            .attr('stroke', d.color || d.line.color)
                            .attr('stroke-opacity', d.colorOpacity || d.line.colorOpacity);
                    } else {
                        target.selectAll('path.line').data([]).exit().remove();
                    }

                    if (d.point || d.bar) {
                        var p = d.point || d.bar;
                        t = target.selectAll('path.symbol').data([true]);
                        t.enter().append('path').classed('symbol', true);
                        t.attr('transform', "translate(" + (x + opts.legend.symbolLength/2) + "," + (y-lp) + ")")
                            .attr('stroke-width', d.lineWidth || p.lineWidth)
                            .attr('stroke', d.color || p.color)
                            .attr('fill', d.fill || p.fill)
                            .attr('stroke-opacity', d.colorOpacity || p.colorOpacity)
                            .attr('d', symbol);
                    } else {
                        target.selectAll('path.symbol').data([]).exit().remove();
                    }

                    t = target.selectAll('text').data([true]);
                    t.enter().append('text');
                    svg_font(t.attr('x', x + dx).attr('y', y).text(d.label), opts.legend.font);

                    if (inline) x += this.getBBox().width + dx;
                });

                var bbox = node.getBBox(),
                    height = Math.ceil(bbox.height + 2*padding),
                    width = Math.ceil(bbox.width + 2*padding);

                var xy = getPosition(group, width, height);


                element.attr("transform", "translate(" + xy[0] + "," + xy[1] + ")");

                box.attr("transform", "translate(" + xy[0] + "," + xy[1] + ")")
                    .attr('x', bbox.x-padding)
                    .attr('y', bbox.y-padding)
                    .attr('height', height)
                    .attr('width', width)
                    .attr('fill', opts.legend.fill)
                    .attr('stroke', opts.legend.color)
                    .attr('lineWidth', opts.legend.lineWidth);
            }

            function CanvasLegend () {
                var labels = getLabels(),
                    group = this.group(),
                    ctx = group.context(),
                    d = opts.legend,
                    font_size = d.font.size,
                    fsize = group.scale(group.dim(font_size)),
                    lp = Math.round(fsize/3),
                    factor = group.factor(),
                    padding = factor*d.padding,
                    textPadding = factor*d.textPadding,
                    spacing = factor*d.symbolPadding,
                    symbolLength = factor*d.symbolLength,
                    symbolSize = Math.ceil(0.333*symbolLength),
                    dx = symbolLength + spacing,
                    dy = fsize + textPadding,
                    inline = inlinePositions.indexOf(d.position) > -1,
                    line = d3.canvas.line(),
                    symbol = d3.canvas.symbol().size(symbolSize*symbolSize),
                    mtxt,
                    width = 0,
                    height = 0;

                ctx.save();
                group.transform(ctx);

                d.font.size = fsize + 'px';
                ctx.font = fontString(d.font);
                d.font.size = font_size;

                ctx.textBaseline = 'middle';

                if (inline) {
                    height = dy;
                    labels.forEach(function (label) {
                        if (width) width += spacing;
                        mtxt = ctx.measureText(label.label);
                        width += dx + mtxt.width;
                    });
                } else {
                    labels.forEach(function (label) {
                        mtxt = ctx.measureText(label.label);
                        width = Math.max(width, dx + mtxt.width);
                        height += dy;
                    });
                }

                var p = 2*(padding + factor*d.lineWidth);
                height = Math.ceil(height + p);
                width = Math.ceil(width + p);

                var xy = getPosition(group, width, height);
                width -= 2*factor*d.lineWidth;
                height -= 2*factor*d.lineWidth;

                // Draw the rectangle containing the legend
                ctx.translate(xy[0], xy[1]);
                ctx.beginPath();
                d3.canvas.drawPolygon(ctx, [[-padding, -padding], [width, -padding], [width, height], [-padding, height]], d.radius);
                ctx.fillStyle = d3.canvas.rgba(d.fill, d.fillOpacity);
                ctx.strokeStyle = d3.canvas.rgba(d.color, d.colorOpacity);
                ctx.lineWidth = factor*d.lineWidth;
                ctx.fill();
                ctx.stroke();

                var x = 0, y = dy/2;

                labels.forEach(function (l) {
                    if (l.line && !l.bar) {
                        line.context(ctx)([[x, y], [x + symbolLength, y]]);
                        ctx.strokeStyle = l.color || l.line.color;
                        ctx.lineWidth = factor*l.line.lineWidth;
                        ctx.stroke();
                    }

                    if (l.point || l.bar) {
                        var p = l.point || l.bar;
                        ctx.save();
                        ctx.translate(x + 0.5*factor*d.symbolLength, y);
                        symbol.context(ctx)();
                        d3.canvas.style(ctx, extend({}, p, l));
                        ctx.restore();
                    }

                    x += dx;
                    ctx.fillStyle = d.color;
                    ctx.fillText(l.label, x, y);

                    if (inline) x += ctx.measureText(l.label).width + spacing;
                    else {
                        x = 0;
                        y += dy;
                    }
                });

                ctx.restore();
            }
        }
    });

    // Line chart
    g.paper.plugin('line', {
        deep: ['active', 'tooltip', 'transition'],

        defaults: {
            interpolate: 'cardinal',
            colorOpacity: 1,
            fillOpacity: 0.4,
            lineWidth: 2,
            fill: 'color',
            active: {}
        },

        init: function (group) {
            var type = group.type();

            // Draw a path or an area
            group.path = function (data, opts) {
                opts || (opts = {});
                chartFormats(group, opts);
                group.drawColor(copyMissing(group.options().line, opts));

                return group.add(g[type].path(group))
                            .pointOptions(pointOptions)
                            .size(point_size)
                            .data(data)
                            .options(opts);
            };
        }
    });

    g.svg.path = function (group) {

        function area_container (aid, create) {
            var b = group.paper().svgBackground(create),
                a = b.select('#' + aid);
            if (!a.size() && create)
                a = b.append('g')
                        .attr('id', aid)
                        .attr("transform", "translate(" + group.marginLeft() + "," + group.marginTop() + ")");
            return a;
        }

        return pathdraw(group, function () {
            var draw = this,
                opts = draw.options(),
                el = group.element(),
                uid = draw.uid(),
                aid = 'area-' + uid,
                p = el.select("#" + uid),
                trans = opts.transition,
                line = this.path_line(),
                data = this.path_data(),
                active, a;

            if (!p.node()) {
                p = el.append('path').attr('id', uid).datum(data);
                if (opts.area)
                    a = area_container(aid, true).append('path').datum(data);
            }
            else {
                p.datum(data);
                a = area_container(aid);
                if (opts.area) {
                    if(!a.size())
                        a = area_container(aid, true);
                    var ar = a.select('path');
                    if (!ar.size())
                        ar = a.append('path');
                    a = ar.datum(data);
                } else {
                    a.remove();
                    a = null;
                }
                if (!group.resizing() && trans && trans.duration) {
                    p = p.transition().duration(trans.duration).ease(trans.ease);
                    if (a)
                        a = a.transition().duration(trans.duration).ease(trans.ease);
                }
            }

            p.attr('d', line)
                .attr('stroke', draw.color)
                .attr('stroke-opacity', draw.colorOpacity)
                .attr('stroke-width', draw.lineWidth)
                .attr('fill', 'none');

            // Area
            if (a) {
                line = draw.path_area();
                if (!draw.fill)
                    draw.fill = draw.color;

                a.attr('d', line)
                 .attr('stroke', 'none');

                if (opts.gradient) {
                    g.gradient().colors([
                        {
                            color: draw.fill,
                            opacity: draw.fillOpacity,
                            offset: 0
                        },
                        {
                            color: draw.fill,
                            opacity: 0,
                            //color: opts.gradient,
                            //opacity: draw.fillOpacity,
                            offset: 100
                        }]).direction('y')(a);
                } else
                    group.setBackground(draw, a);
            }

            //
            // Activate mouse over events on control points
            if (draw.active && draw.active.symbol)
                group.events(group.paper().element(), uid, function () {
                    if (!active)
                        active = el.append('path')
                                    .attr('id', 'point-' + uid)
                                    .datum(g.svg.point(draw, [], 0))
                                    .attr('d', draw.symbol);
                    var mouse = d3.mouse(this),
                        x = mouse[0] - group.marginLeft(),
                        d = draw.bisect(x);
                    if (d) {
                        active.attr("transform", "translate(" + d.sx + "," + d.sy + ")");
                        active.datum().data = d.data;
                        return active.node();
                    }
                });

            return p;
        });
    };

    g.canvas.path = function (group) {
        var d = canvasMixin(pathdraw(group)),
            scalex = d.scalex,
            scaley = d.scaley,
            opts, data, active, ctx;

        d.render = function () {
            opts = d.options();
            data = d.path_data();
            ctx = d.context();

            ctx.save();
            group.transform(ctx);

            if (opts.area) {
                var background = group.paper().canvasBackground(true).node().getContext('2d');
                background.save();
                group.transform(background);
                if (!d.fill) d.fill = d.color;
                d.path_area().context(background)(data);

                if (opts.gradient) {
                    var scale = group.yaxis().scale(),
                        domain = scale.domain();
                    g.gradient()
                            .y1(scale(domain[domain.length-1]))
                            .y2(scale(domain[0]))
                            .direction('y')
                            .colors([
                            {
                                color: d3.canvas.rgba(d.fill, d.fillOpacity),
                                offset: 0
                            },
                            {
                                color: d3.canvas.rgba(opts.gradient, d.fillOpacity),
                                offset: 100
                            }])(d3.select(background.canvas));
                } else {
                    background.fillStyle = d3.canvas.rgba(d.fill, d.fillOpacity);
                    background.fill();
                }
                background.restore();
            }
            ctx.strokeStyle = d.color;
            ctx.lineWidth = group.factor()*d.lineWidth;
            d.path_line().context(ctx)(data);
            ctx.stroke();
            ctx.restore();
            return d;
        };

        d.inRange = function (ex, ey) {
            var opts = d.options();
            if (!d.active) return false;
            if(!d.active.symbol) return false;
            if (!active)
                active = g.canvas.point(d, [], 0);
            var dd = d.bisect(ex - group.marginLeft());
            if (dd) {
                active.data = dd.data;
                return active;
            }
            return false;
        };

        return d;
    };


    function pathdraw(group, render, draw) {
        var type = group.type(),
            bisector = d3.bisector(function (d) {return d.sx;}).left,
            data, ordered;

        draw = drawing(group, render, draw);

        draw.bisector = d3.bisector(function (d) {return d.sx;}).left;

        draw.each = function (callback) {
            callback.call(draw);
            return draw;
        };

        draw.path_line = function () {
            var opts = draw.options();

            return d3[type].line()
                            .interpolate(opts.interpolate)
                            .x(function (d) {return d.sx;})
                            .y(function (d) {return d.sy;});
        };

        draw.path_area = function () {
            var opts = draw.options(),
                scaley = group.yaxis().scale();

            return d3[type].area()
                                .interpolate(opts.interpolate)
                                .x(function (d) {return d.sx;})
                                .y0(scaley(scaley.domain()[0]))
                                .y1(function (d) {return d.sy;});
        };

        draw.path_data = function () {
            var sx = draw.x(),
                sy = draw.y(),
                scalex = group.xaxis().scale(),
                scaley = group.yaxis().scale();

            ordered = null;
            draw.symbol = d3[type].symbol().type(function (d) {return d.symbol || 'circle';})
                                           .size(draw.size());
            data = draw.data().map(function (d, i) {
                var xy = {
                    x: sx(d),
                    y: sy(d),
                    index: i,
                    data: d
                };
                xy.sx = scalex(xy.x);
                xy.sy = scaley(xy.y);
                return xy;
            });
            return data;
        };

        draw.bisect = function (x) {
            if (!ordered && data)
                ordered = data.slice().sort(function (a, b) {return d3.ascending(a.sx, b.sx);});
            if (ordered) {
                var index = bisector(ordered, x);
                if (index < ordered.length)
                    return ordered[index];
            }
        };

        return draw;
    }

    //
    //  Giotto Context Menu
    //
    //  Returns a function which can be used to bind the context menu to
    //  a node element.
    g.contextMenu = function () {
        var element = null,
            menuElement = null,
            opened = false,
            disabled = false,
            events = d3.dispatch('open', 'close');

        function menu (target, callback) {
            init();
            target
                .on('keyup.gmenu', handleKeyUpEvent)
                .on('click.gmenu', handleClickEvent)
                .on('contextmenu.gmenu', handleContextMenu(callback));
        }

        menu.disabled  = function (x) {
            if (!arguments.length) return disabled;
            disabled = x ? true : false;
            return menu;
        };

        d3.rebind(menu, events, 'on');

        return menu;

        // INTERNALS

        function handleKeyUpEvent () {
            if (!disabled && opened && d3.event.keyCode === 27)
                close();
        }

        function handleClickEvent () {
            var event = d3.event;
            if (!disabled && opened && event.button !== 2 || event.target !== element)
                close();
        }

        function handleContextMenu (callback) {
            if (callback)
                return function () {
                    if (disabled) return;
                    var event = d3.event;
                    event.preventDefault();
                    event.stopPropagation();
                    close();
                    element = this;
                    open(event, callback);
                };
        }

        function open (event, callback) {
            if (callback) callback(menuElement);
            menuElement.classed('open', true);

            var docLeft = (window.pageXOffset || document.scrollLeft || 0) - (document.clientLeft || 0),
                docTop = (window.pageYOffset || document.scrollTop || 0) - (document.clientTop || 0),
                elementWidth = menuElement.node().scrollWidth,
                elementHeight = menuElement.node().scrollHeight,
                docWidth = document.clientWidth + docLeft,
                docHeight = document.clientHeight + docTop,
                totalWidth = elementWidth + event.pageX,
                totalHeight = elementHeight + event.pageY,
                left = Math.max(event.pageX - docLeft, 0),
                top = Math.max(event.pageY - docTop, 0);

            if (totalWidth > docWidth)
                left = left - (totalWidth - docWidth);

            if (totalHeight > docHeight)
                top = top - (totalHeight - docHeight);

            menuElement.style({
                top: top + 'px',
                left: left + 'px',
                position: 'fixed'
            });
            opened = true;
        }

        function close () {
            menuElement.classed('open', false);
            if (opened)
                events.close();
            opened = false;
        }

        function init () {
            if (!menuElement) {

                menuElement = d3.select(document.createElement('div'))
                                .attr('class', 'giotto-menu');
                close();
                document.body.appendChild(menuElement.node());

                d3.select(document)
                    .on('keyup.gmenu', handleKeyUpEvent)
                    // Firefox treats a right-click as a click and a contextmenu event
                    // while other browsers just treat it as a contextmenu event
                    .on('click.gmenu', handleClickEvent)
                    .on('contextmenu.gmenu', handleClickEvent);
            }
        }

    };

    //
    // Context menu singletone
    g.contextmenu = g.contextMenu();


    //
    //  Context Menu Plugin for Visualization
    //  ==========================================
    //
    //  * layout create the html layout
    //  * itms is a list of options to display
    g.viz.plugin('menu', {

        defaults: {
            layout: function (viz, menu, items) {
                menu.append('ul')
                    .attr({'class': 'dropdown-menu',
                           'role': 'menu'})
                    .selectAll('li')
                    .data(items)
                    .enter()
                    .append('li').attr('role', 'presentation')
                    .append('a').attr('role', 'menuitem').attr('href', '#')
                    .text(function (d) {return isFunction(d.label) ? d.label() : d.label;})
                    .on('click', function (d) {
                        if (d.callback) d.callback(viz);
                    });
            },
            items: null
        },

        init: function (viz) {

            viz.on('tick.menu', function () {
                var opts = viz.options();
                if (opts.menu.items)
                    g.contextmenu(viz.element(), function (menu) {
                        menu.select('*').remove();
                        return opts.menu.layout(viz, menu, opts.menu.items);
                    });
                else
                    g.contextmenu(viz.element());
            });
        }
    });


    // Add pie charts to giotto groups

    g.paper.plugin('pie', {
        deep: ['active', 'tooltip', 'labels', 'transition'],

        defaults: {
            lineWidth: 1,
            // pad angle in degrees
            padAngle: 0,
            cornerRadius: 0,
            fillOpacity: 0.7,
            colorOpacity: 1,
            innerRadius: 0,
            startAngle: 0,
            formatX: d3_identity,
            formatPercent: ',.2%',
            active: {
                fill: 'darker',
                color: 'brighter',
                //innerRadius: 100%,
                //outerRadius: 105%,
                fillOpacity: 1
            },
            tooltip: {
                template: function (d) {
                    return "<p><strong>" + d.x + "</strong> " + d.y + "</p>";
                }
            },
            labels: {
                show: true,
                position: 'ouside',
                outerRadius: 1.05,
                color: '#333',
                colorOpacity: 0.5,
                lineWidth: 1
            }
        },

        init: function (group) {
            var type = group.type(),
                arc = d3[type].arc()
                                .innerRadius(function (d) {return d.innerRadius;})
                                .outerRadius(function (d) {return d.outerRadius;});

            // add a pie chart drawing to the group
            group.pie = function (data, opts) {
                opts || (opts = {});
                chartFormats(group, opts);
                copyMissing(group.options().pie, opts);

                var draw = group.add(function () {

                    var width = group.innerWidth(),
                        height = group.innerHeight(),
                        opts = this.options(),
                        outerRadius = 0.5*Math.min(width, height),
                        innerRadius = opts.innerRadius*outerRadius,
                        cornerRadius = group.scale(group.dim(opts.cornerRadius)),
                        value = this.y(),
                        data = this.data(),
                        pie = d3.layout.pie().value(function (d) {return value(d.data);})
                                             .padAngle(d3_radians*opts.padAngle)
                                             .startAngle(d3_radians*opts.startAngle)(data),
                        d, dd;

                    this.arc = arc.cornerRadius(cornerRadius);

                    // recalculate pie angles
                    for (var i=0; i<pie.length; ++i) {
                        d = pie[i];
                        dd = d.data;
                        dd.set('innerRadius', innerRadius);
                        dd.set('outerRadius', outerRadius);
                        delete d.data;
                        data[i] = extend(dd, d);
                    }

                    return g[type].pie(this, width, height);
                });

                return draw.pointOptions(extendArray(['innerRadius', 'outerRadius'], drawingOptions))
                            .dataConstructor(pie_costructor)
                            .options(opts)
                            .data(data);
            };
        }
    });

    var pie_costructor = function (rawdata) {
        var draw = this,
            x = draw.x(),
            pieslice = g[draw.group().type()].pieslice,
            map = d3.map(this.data() || [], function (d) {return x(d.data);}),
            data = [],
            slice;
        rawdata.forEach(function (d) {
            slice = map.get(x(d));
            if (!slice) slice = pieslice(draw, d);
            else slice.data = d;
            data.push(slice);
        });
        return data;
    };

    function midAngle(d) {
        return d.startAngle + (d.endAngle - d.startAngle)/2;
    }

    function pieSlice (draw, data, d) {
        // Default values
        var dd = isArray(data) ? d : data,
            group = draw.group(),
            factor = group.factor(),
            target = group.paper().element().node();

        dd.fill = dd.fill || draw.group().pickColor();
        dd.color = dd.color || d3.rgb(dd.fill).darker().toString();

        d = drawingData(draw, data, d);
        if (group.type() === 'canvas') d = canvasMixin(d);

        d.bbox = function () {
            var bbox = target.getBoundingClientRect(),
                c1 = Math.sin(d.startAngle),
                s1 = Math.cos(d.startAngle),
                c2 = Math.sin(d.endAngle),
                s2 = Math.cos(d.endAngle),
                cc = Math.sin(0.5*(d.startAngle + d.endAngle)),
                sc = Math.cos(0.5*(d.startAngle + d.endAngle)),
                r1 = d.innerRadius,
                r2 = d.outerRadius,
                rc = 0.5*(r1 + r2),
                left = group.marginLeft() + 0.5*group.innerWidth(),
                top = group.marginTop() + 0.5*group.innerHeight(),
                f = 1/factor;
            return {
                nw: {x: xx(r2*c1), y: yy(r2*s1)},
                ne: {x: xx(r2*c2), y: yy(r2*s2)},
                se: {x: xx(r1*c2), y: yy(r1*s2)},
                sw: {x: xx(r1*c1), y: yy(r1*s1)},
                w: {x: xx(rc*c1), y: yy(rc*s1)},
                n: {x: xx(r2*cc), y: yy(r2*sc)},
                e: {x: xx(rc*c2), y: yy(rc*s2)},
                s: {x: xx(r1*cc), y: yy(r1*sc)},
                c: {x: xx(rc*cc), y: yy(rc*sc)},
                tooltip: 's'
            };

            function xx(x) {return Math.round(f*(left + x) + bbox.left);}
            function yy(y) {return Math.round(f*(top - y) + bbox.top);}
        };

        return d;
    }

    g.svg.pie = function (draw, width, height) {

        var group = draw.group(),
            container = group.element(),
            opts = draw.options(),
            trans = opts.transition,
            pp = container.select('#' + draw.uid()),
            resizing = group.resizing();

        if (!pp.size()) {
            resizing = true;
            pp = container.append("g")
                        .attr('id', draw.uid())
                        .classed('pie', true);
            pp.append('g').classed('slices', true);
        }

        var slices = pp.attr("transform", "translate(" + width/2 + "," + height/2 + ")")
                        .select('.slices')
                        .selectAll(".slice").data(draw.data());

        slices.enter()
            .append("path")
            .attr('class', 'slice');

        slices.exit().remove();

        group.events(slices);

        if (opts.labels.show)
            g.svg.pielabels(draw, pp, opts);

        if (!resizing && trans && trans.duration)
            slices = slices.transition().duration(trans.duration).ease(trans.ease);

        return group.draw(slices.attr('d', draw.arc));
    };

    g.svg.pieslice = function (draw, data) {
        var group = draw.group(),
            p = pieSlice(draw, data, {});

        p.render = function (element) {
            group.draw(element).attr('d', draw.arc);
        };

        return p;
    };

    g.svg.pielabels = function (draw, container, options) {
        var group = draw.group(),
            opts = extend({}, draw.group().options().font, options.labels),
            labels = container.selectAll('.labels'),
            trans = options.transition,
            resizing = group.resizing(),
            pcf = d3.format(options.formatPercent);

        if (!labels.size()) {
            resizing = true;
            labels = container.append('g').classed('labels', true);
        }

        if (opts.position === 'bar') {

        } else {
            var x = draw.x(),
                text = labels.selectAll('text').data(draw.data()),
                pos;
            text.enter().append("text");
            text.exit().remove();
            svg_font(text, opts);

            if (!resizing && trans && trans.duration)
                text = text.transition().duration(trans.duration).ease(trans.ease);

            if (opts.position === 'outside') {
                var outerArc = d3.svg.arc(),
                    lines = container.selectAll('.lines').data([true]),
                    radius,
                    xx;

                lines.enter().append('g').classed('lines', true);
                lines = lines.selectAll('polyline').data(draw.data());
                lines.enter().append('polyline');
                lines.exit().remove();

                if (!resizing && trans && trans.duration)
                    lines = lines.transition().duration(trans.duration).ease(trans.ease);

                var right = [],
                    left = [];
                draw.data().forEach(function (d) {
                    d.labelAngle = midAngle(d);
                    d.labelRadius = d.outerRadius*opts.outerRadius;
                    d.labelTurn = outerArc.innerRadius(d.labelRadius).outerRadius(d.labelRadius).centroid(d);
                    d.labelY = d.labelTurn[1];
                    d.labelAngle < π ? right.push(d) : left.push(d);
                });
                relax(right);
                relax(left);
                lines.attr('points', function (d) {
                        pos = [1.05 * d.labelRadius * (d.labelAngle < π ? 1 : -1), d.labelY];
                        return [draw.arc.centroid(d), d.labelTurn, pos];
                    }).attr('fill', 'none')
                    .attr('stroke', opts.color)
                    .attr('stroke-opacity', opts.colorOpacity)
                    .attr('stroke-width', opts.lineWidth);

                text.text(function (d) {
                        return x(d.data) + ' ' + pcf(pc(d));
                    })
                    .attr('transform', function (d) {
                        pos = [1.1 * d.labelRadius * (d.labelAngle < π ? 1 : -1), d.labelY];
                        return 'translate(' + pos + ')';
                    })
                    .style('text-anchor', function (d) {
                        return midAngle(d) < π ? "start":"end";
                    });
            }
        }

        function pc (d) {
            return (d.endAngle - d.startAngle)/τ;
        }

        function relax (nodes) {
            var N = nodes.length,
                tol = 10000,
                maxiter = 100;
            if (N < 3) return;
            var ymin = group.innerHeight()/2 + group.marginTop(),
                ymax = group.innerHeight()/2 + group.marginBottom(),
                iter = 0,
                dy, y0, y1;

            nodes.sort(function (a, b) {return d3.ascending(a.labelY, b.labelY);});

            ymin = Math.min(nodes[0].labelY, -ymin+10);
            ymax = Math.max(nodes[N-1].labelY, ymax-10);

            while (tol > 0.5 && iter<maxiter) {
                y1 = nodes[0].labelY;
                iter++;
                tol = 0;
                nodes[0].dy = 0;
                for (var i=1; i<nodes.length; ++i) {
                    y0 = y1;
                    y1 = nodes[i].labelY;
                    dy = force(y1-y0);
                    nodes[i-1].dy -= dy;
                    nodes[i].dy = dy;
                }
                for (i=1; i<nodes.length-1; ++i) {
                    if (nodes[i].dy < 0)
                        dy = Math.max(nodes[i].dy, 0.49*(nodes[i-1].labelY - nodes[i].labelY));
                    else
                        dy = Math.min(nodes[i].dy, 0.49*(nodes[i+1].labelY - nodes[i].labelY));
                    tol = Math.max(tol, abs(dy));
                    nodes[i].labelY += dy;
                }
                nodes[0].labelY = Math.max(nodes[0].labelY + nodes[0].dy, ymin);
                nodes[N-1].labelY = Math.min(nodes[N-1].labelY + nodes[N-1].dy, ymax);
            }

            function force (dd) {
                return dd < 20 ? 100/(dd*dd) : 0;
            }
        }
    };

    g.canvas.pie = function (draw) {
        draw.each(function () {
            this.reset().render();
        });
    };

    g.canvas.pieslice = function (draw, data) {
        var d = pieSlice(draw, data, {}),
            group = draw.group(),
            factor = draw.factor();

        d.render = function () {
            return _draw(function (ctx) {
                d3.canvas.style(ctx, d);
                return d;
            });
        };

        d.inRange = function (ex, ey) {
            return _draw(function (ctx) {
                return ctx.isPointInPath(ex, ey);
            });
        };

        return d;

        function _draw (callback) {
            var ctx = d.context();
            ctx.save();
            group.transform(ctx);
            ctx.translate(0.5*group.innerWidth(), 0.5*group.innerHeight());
            draw.arc.context(ctx)(d);
            var r = callback(ctx);
            ctx.restore();
            return r;
        }
    };


    // Scapper point chart
    g.paper.plugin('point', {
        deep: ['active', 'tooltip', 'transition'],

        defaults: {
            symbol: 'circle',
            size: '8px',
            fill: true,
            fillOpacity: 1,
            colorOpacity: 1,
            lineWidth: 2,
            active: {
                fill: 'darker',
                color: 'brighter',
                // Multiplier for size, set to 100% for no change
                size: '150%'
            },
            transition: extend({}, g.defaults.transition)
        },

        init: function (group) {
            var type = group.type();

            // Draw points in the group
            group.points = function (data, opts) {
                opts || (opts = {});
                chartFormats(group, opts);
                group.drawColor(copyMissing(group.options().point, opts));

                return group.add(g[type].points)
                    .pointOptions(pointOptions)
                    .size(point_size)
                    .options(opts)
                    .dataConstructor(point_costructor)
                    .data(data);
            };
        }
    });


    var SymbolSize = {
            circle: 0.7,
            cross: 0.7,
            diamond: 0.7,
            "triangle-up": 0.6,
            "triangle-down": 0.6
        },

        pointOptions = extendArray(['size', 'symbol'], drawingOptions),

        point_size = function (d) {
            var s = +d.size;
            if (isNaN(s)) {
                var g = d.group();
                s = g.scale(g.xfromPX(d.size.substring(0, d.size.length-2)));
            }
            return s*s*(SymbolSize[d.symbol] || 1);
        },

        point_costructor = function (rawdata) {
            var draw = this,
                group = this.group(),
                size = group.scale(group.dim(this.options().size)),
                point = g[group.type()].point,
                data = [];

            rawdata.forEach(function (d) {
                data.push(point(draw, d, size));
            });
            return data;
        };

    g.svg.point = function (draw, data, size) {
        var d = drawingData(draw, data),
            group = draw.group();

        d.set('size', data.size === undefined ? size : data.size);
        d.render = function (element) {
            group.draw(element).attr('d', draw.symbol);
        };
        return d;
    };

    g.svg.points = function () {
        var group = this.group(),
            pp = group.element().select("#" + this.uid()),
            scalex = this.scalex(),
            scaley = this.scaley(),
            data = this.data();

        this.symbol = d3.svg.symbol().type(function (d) {return d.symbol;})
                                     .size(this.size());

        if (!pp.node()) {
            pp = group.element().append('g').attr('id', this.uid());
            this.remove = function () {
                pp.remove();
            };
        }

        var points = pp.selectAll('*').data(this.data());
        points.enter().append('path');
        points.exit().remove();

        group.events(group.draw(points
                 .attr("transform", function(d) {
                     return "translate(" + scalex(d.data) + "," + scaley(d.data) + ")";
                 })
                 .attr('d', this.symbol)));

        return pp;
    };

    g.canvas.points = function () {
        this.each(function () {
            this.reset().render();
        });
    };

    g.canvas.point = function (draw, data, size) {
        var d = canvasMixin(drawingData(draw, data)),
            scalex = draw.scalex(),
            scaley = draw.scaley(),
            factor = draw.factor(),
            group = draw.group();

        function symbol () {
            if (!draw.Symbol)
                draw.Symbol = d3.canvas.symbol().type(function (d) {return d.symbol;})
                                                .size(draw.size());
            return draw.Symbol;
        }

        d.set('size', data.size === undefined ? size : data.size);

        d.render = function () {
            return _draw(function (ctx) {
                d3.canvas.style(ctx, d);
                return d;
            });
        };

        d.inRange = function (ex, ey) {
            return _draw(function (ctx) {
                return ctx.isPointInPath(ex, ey);
            });
        };

        d.bbox = function () {
            var x = scalex(d.data) + group.marginLeft(),
                y = scaley(d.data) + group.marginTop(),
                size = Math.sqrt(symbol().size()(d));
            return canvasBBox(d, [x-size, y-size], [x+size, y-size], [x+size, y+size], [x-size, y+size]);
        };

        return d;

        function _draw (callback) {
            var ctx = d.context();
            ctx.save();
            group.transform(ctx);
            ctx.translate(scalex(d.data), scaley(d.data));
            symbol().context(ctx)(d);
            var r = callback(ctx);
            ctx.restore();
            return r;
        }
    };

    //
    //  Add zoom functionality to charts

    // Add zoom to the events triggered by a group
    g.constants.groupEvents.push('zoom');

    g.chart.plugin('zoom', {

        defaults: {
            x: false,
            y: false,
            scaleExtent: [1, 10]
        },

        init: function (chart) {
            // internal flag indicating if chart is zooming
            var zooming = false;

            // Return true whan the chart is performing a zoom operation
            chart.zooming = function () {
                return zooming;
            };

            // Enable zoom on the chart
            // only when either zoom.x or zoom.y are enabled
            chart.enableZoom = function () {

                var opts = chart.options().zoom,
                    zoom = d3.behavior.zoom()
                        .on('zoom', function () {
                            zooming = true;
                            chart.each(function (serie) {
                                zoomGroup(zoom, serie.group(), opts);
                            });
                            zooming = false;
                        });

                if (opts.scaleExtent)
                    zoom.scaleExtent(opts.scaleExtent);

                // Apply the zoom behavior to the chart container
                // This means each single group should handle the event separately
                zoom(chart.element());
            };

            chart.on('tick.zoom', function () {
                var zoom = chart.options().zoom;
                if (zoom.x || zoom.y)
                    chart.enableZoom();
            });

            // INTERNALS


            // Perform zoom for one group
            function zoomGroup (zoom, group, opts) {
                if (opts.x) {
                    zoom.x(group.xaxis().scale());
                }
                if (opts.y) {
                    zoom.y(group.yaxis().scale());
                }
                group.render();
            }

            function __() {
                var factor = grid.factor();

                if (factor === 1) {
                    if (opts.grid.zoomx)
                        zoom.x(grid.xaxis().scale());

                    if (opts.grid.zoomy)
                        zoom.y(grid.yaxis().scale());
                } else {

                    if (opts.grid.zoomx) {
                        scalex = grid.xaxis().scale().copy();
                        var x1 = scalex.invert(-factor*opts.margin.left),
                            x2 = scalex.invert(factor*(opts.size[0] - opts.margin.left));
                        scalex.domain([x1, x2]).range([0, opts.size[0]]);
                        zoom.x(scalex);
                    }

                    if (opts.grid.zoomy) {
                        scaley = grid.yaxis().scale().copy();
                        var y1 = scaley.invert(-factor*opts.margin.left),
                            y2 = scaley.invert(factor*(opts.size[1] - opts.margin.bottom));
                        scaley.domain([y1, y2]).range([opts.size[1], 0]);
                        zoom.y(scaley);
                    }
                }
            }
        }
    });

var NS = NS || {};
NS["src/text/giotto.min.css"] = '@charset "UTF-8";.sunburst text{z-index:9999}.sunburst path{stroke:#fff;fill-rule:evenodd}.axis,.d3-slider-axis line{shape-rendering:crispEdges;fill:none}.line{fill:none}.d3-tip:after{line-height:1;width:100%;font-size:16px;position:absolute;display:inline;-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box}.d3-tip.n:after{margin:-2px 0 0;top:100%;content:"\\25BC";left:0;text-align:center}.d3-tip.e:after{margin:-4px 0 0;top:50%;content:"\\25C0";left:-8px}.d3-tip.s:after{margin:0 0 2px;top:-8px;content:"\\25B2";left:0;text-align:center}.d3-tip.w:after{margin:-4px 0 0 -1px;top:50%;content:"\\25B6";left:100%}.d3-slider{margin:20px;font-family:Verdana,Arial,sans-serif;font-size:1.1em;position:relative;z-index:2;border:1px solid}.d3-slider-horizontal{height:.8em}.d3-slider-horizontal.d3-slider-axis{margin-bottom:30px}.d3-slider-range{right:0;left:0;position:absolute;height:.8em}.d3-slider-range-vertical{right:0;top:0;left:0;position:absolute}.d3-slider-range-vertical.d3-slider-axis{margin-right:30px}.d3-slider-vertical{width:.8em;height:100px}.d3-slider-handle{width:1.2em;height:1.2em;position:absolute;z-index:3;-webkit-border-radius:4px;-moz-border-radius:4px;border-radius:4px;border:1px solid}.d3-slider-horizontal .d3-slider-handle{top:-.25em;margin-left:-.6em}.d3-slider-axis{z-index:1;position:relative}.d3-slider-axis-bottom{top:.8em}.d3-slider-axis-right{left:.8em}.d3-slider-axis path{fill:none;stroke-width:0}.d3-slider-axis text{font-size:11px}.d3-slider-vertical .d3-slider-handle{margin-bottom:-.6em;margin-left:0;left:-.25em}.d3-slider-default{border-color:#aaa}.d3-slider-default .d3-slider-handle{background-color:#ddd;background-image:-moz-linear-gradient(top,#eee,#ddd);background-image:-ms-linear-gradient(top,#eee,#ddd);background-image:-webkit-gradient(linear,0 0,0 100%,from(#eee),to(#ddd));background-image:-webkit-linear-gradient(top,#eee,#ddd);background-image:-o-linear-gradient(top,#eee,#ddd);background-image:linear-gradient(top,#eee,#ddd);background-repeat:repeat-x;filter:progid:DXImageTransform.Microsoft.gradient(startColorstr=\'#eee\', endColorstr=\'#ddd\', GradientType=0);border-color:#aaa}';

    // load Css unless blocked
    if (root.giottostyle !== false) {
        var giottostyle = document.createElement("style");
        giottostyle.innerHTML = NS["src/text/giotto.min.css"];
        document.getElementsByTagName("head")[0].appendChild(giottostyle);
    }

    //
    //  Optional Angular Integration
    //  ==================================
    //
    //  To create the angular module containing giotto directive:
    //
    //      d3.giotto.angular.module(angular)
    //
    //  To add all visualizations to the module
    //
    //      d3.giotto.angular.addAll()
    //
    //  To register the module and add all visualizations
    //
    //      d3.giotto.angular.module(angular).addAll();
    //
    g.angular = (function () {
        var ag = {},
            mod;

        // Mixin for adding scope method to visualization objects
        ag.mixin = function (d) {
            var scope;

            d.scope = function (_) {
                if (!arguments.length) return scope;
                var opts = d.options();
                scope = _;
                if (isFunction(opts.angular))
                    opts.angular(d, opts);

                return d;
            };

            if (d.tick) {
                var tick = d.tick;

                d.tick = function() {
                    if (scope && scope.stats)
                        scope.stats.begin();
                    tick();
                    if (scope && scope.stats)
                        scope.stats.end();
                };
            }

            return d;
        };

        //
        //  Get Options for a Visualization Directive
        //  ==============================================
        //
        //  Obtain information from
        //  * javascript object
        //  * element attributes
        //  * scope variables
        ag.getOptions = function (scope, attrs, name) {
            var key = attrs[name],
                exclude = [name, 'options', 'class', 'style'],
                jsOptions;

            if (typeof attrs.options === 'string')
                key = attrs.options;

            // Try the scope first
            if (key) {
                jsOptions = scope[key];

                // try the global javascript object
                if (!jsOptions)
                    jsOptions = getRootAttribute(key);
            }

            if (typeof jsOptions === 'function')
                jsOptions = jsOptions();

            if (!jsOptions) jsOptions = {};

            var attrOptions = {};
            forEach(attrs, function (value, name) {
                if (name.substring(0, 1) !== '$' && exclude.indexOf(name) === -1)
                    attrOptions[name] = value;
            });
            return {js: jsOptions, attr: attrOptions};
        };

        ag.module = function (angular, moduleName, deps) {

            if (!arguments.length) return mod;

            if (!mod) {
                moduleName = moduleName || 'giotto';
                deps = deps || [];

                mod = angular.module(moduleName, deps);

                mod.config(['$compileProvider', function (compileProvider) {

                        mod.directive = function (name, factory) {
                            compileProvider.directive(name, factory);
                            return (this);
                        };

                    }])

                    //
                    //  Giotto Visualization Collection
                    //  ====================================
                    //
                    //  Directive to aggregate giotto visualizations with
                    //  close interaction
                    .directive('giottoCollection', function () {

                        return {
                            restrict: 'AE',

                            controller: ['$scope', function (scope) {
                                scope.giottoCollection = ag.mixin(g.viz.collection());
                            }],

                            link: function (scope, element, attrs) {
                                var o = ag.getOptions(scope, attrs, 'giottoCollection');
                                scope.giottoCollection
                                    .options(o.attr)
                                    .options(o.js)
                                    .scope(scope).start();
                            }
                        };
                    })

                    // Directive to privide frame stats
                    .directive('jstats', function () {
                        return {
                            link: function (scope, element, attrs) {
                                var mode = attrs.mode ? +attrs.mode : 1;
                                require(['stats'], function () {
                                    var stats = new Stats();
                                    stats.setMode(mode);
                                    scope.stats = stats;
                                    element.append(angular.element(stats.domElement));
                                });
                            }
                        };
                    });
            }
            return ag;
        };

        ag.directive = function (vizType, name, injects) {

            if (!mod) {
                g.log.warn('No angular module, cannot add directive');
                return;
            }

            injects = injects ? injects.slice() : [];

            // Create directive from Viz name if not provided
            name = mod.name.toLowerCase() + name.substring(0,1).toUpperCase() + name.substring(1);

            function startViz(scope, element, o, options, injected) {
                var collection = scope.giottoCollection,
                    key;

                // Get the key for the collection (if a collection is available)
                if (collection) {
                    if (isString(options)) {
                        key = options;
                        options = null;
                    } else
                        key = collection.size() + 1;
                }

                // Add injects to the scope object
                for (var i=0; i<injected.length; ++i)
                    scope[injects[i]] = injected[i];

                // Creat the visualization
                var viz = vizType(element[0], o.attr)
                            .options(o.js)
                            .options(options);
                //
                // Add angular functions
                viz = ag.mixin(viz).scope(scope);

                element.data(name, viz);

                if (collection)
                    collection.set(key, viz);
                else {
                    scope.$emit('giotto-viz', viz);
                    viz.start();
                }
            }

            //  Directive implementation for a visualization other than a
            //  collection
            injects.push(function () {
                var injected_arguments = arguments;
                return {
                    //
                    // Create via element tag or attribute
                    restrict: 'AE',
                    //
                    link: function (scope, element, attrs) {
                        var viz = element.data(name);
                        if (!viz) {
                            var key = attrs[name],
                                o = ag.getOptions(scope, attrs, name),
                                deps = o.js.require || o.attr.require;
                            if (deps) {
                                if (!g._.isArray(deps)) deps = [deps];
                                require(deps, function (opts) {
                                    startViz(scope, element, o, opts, injected_arguments);
                                });
                            } else {
                                startViz(scope, element, o, key, injected_arguments);
                            }
                        }
                    }
                };
            });

            return mod.directive(name, injects);
        };

        //  Load all visualizations into angular 'giotto' module
        ag.addAll = function (injects) {
            //
            // Loop through d3 extensions and create directives
            // for each Visualization class
            g.log.info('Adding giotto visualization directives');

            angular.forEach(g.viz, function (vizType) {
                var name = vizType.vizName ? vizType.vizName() : null;
                if (name && name !== 'collection')
                    g.angular.directive(vizType, name, injects);
            });

            return ag;
        };

        return ag;
    }());

    g.defaults.crossfilter = {
        tolerance: 1.1
    };

    //
    //  Add Crossfilter integration
    //  params opts
    //      - data: multidimensional data
    //      - callback: Optional callback to invoke once the crossfilter is loaded
    g.crossfilter = function (opts) {
        var cf = extend({}, g.defaults.crossfilter, opts);

        var data = opts.data,
            callback = opts.callback;

        cf.dims = {};

        // Add a new dimension to the crossfilter
        cf.dimension = function (name, callback) {
            if (!callback) {
                callback = function (d) {
                    return d[name];
                };
            }
            cf.dims[name] = cf.data.dimension(callback);
        };

        // Reduce the number of points by using a K-mean clustering algorithm
        cf.reduceDensity = function (dimension, points, start, end) {
            var count = 0,
                dim = cf.dims[dimension],
                group;

            if (!dim)
                throw Error('Cross filter dimension "' + dimension + '"" not available. Add it with the addDimension method');

            if (start === undefined) start = null;
            if (end === undefined) end = null;

            if (start === null && end === null)
                group = dim.filter();
            else
                group = dim.filter(function (d) {
                    if (start !== null && d < start) return;
                    if (end !== null && d > end) return;
                    return true;
                });

            var all = group.bottom(Infinity);

            if (all.length > cf.tolerance*points) {
                var km = g.math.kmeans(),
                    reduced = [],
                    cl = [],
                    centroids = [],
                    r = all.length / points,
                    index, i, c;

                // Create the input for the k-means algorithm
                for (i=0; i<all.length; i++)
                    cl.push([all[i][dimension]]);

                for (i=0; i<points; i++) {
                    centroids.push(cl[Math.round(i*r)]);
                }

                km.centroids(centroids).maxIters(10);

                cl = km.cluster(cl).sort(function (a, b) {
                    return a.centroid[0] - b.centroid[0];
                });

                cl.forEach(function (d) {
                    index = d.indices[0];
                    c = d.points[0];
                    for (i=1; i<d.points.length; ++i) {
                        if (d.points[i] > c) {
                            index = d.indices[i];
                            c = d.points[i];
                        }
                    }
                    reduced.push(all[index]);
                });
                all = reduced;
            }

            return all;
        };


        function build () {
            if (!g.crossfilter.lib)
                throw Error('Could not find crossfilter library');

            // convert data to crossfilter data
            cf.data = g.crossfilter.lib(data);

            if (g._.isArray(opts.dimensions))
                opts.dimensions.forEach(function (o) {
                    cf.dimension(o);
                });

            if (callback) callback(cf);
        }

        if (g.crossfilter.lib === undefined)
            if (typeof crossfilter === 'undefined') {
                require(['crossfilter'], function (crossfilter) {
                    g.crossfilter.lib = crossfilter || null;
                    build();
                });
                return cf;
            }
            else {
                g.crossfilter.lib = crossfilter;
            }

        build();
        return cf;
    };


    //
    //  Leaflet Integration
    //  =============================
    //
    g.geo.leaflet = function (element, opts) {

        if (typeof L === 'undefined') {
            g._.loadCss(g.constants.leaflet);
            g.require(['leaflet'], function () {
                viz.start();
            });
        } else {
            var map = new L.map(element, {
                center: opts.center,
                zoom: opts.zoom
            });
            if (opts.zoomControl) {
                if (!opts.wheelZoom)
                    map.scrollWheelZoom.disable();
            } else {
                map.dragging.disable();
                map.touchZoom.disable();
                map.doubleClickZoom.disable();
                map.scrollWheelZoom.disable();

                // Disable tap handler, if present.
                if (map.tap) map.tap.disable();
            }

            // Attach the view reset callback
            map.on("viewreset", function () {
                for (var i=0; i<callbacks.length; ++i)
                    callbacks[i]();
            });

            viz.resume();
        }
        d3.geo.transform({point: LeafletProjectPoint});

        function LeafletProjectPoint (x, y) {
            var point = map.latLngToLayerPoint(new L.LatLng(y, x));
            this.stream.point(point.x, point.y);
        }
    };


    return d3;
}));