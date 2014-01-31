/**
 * SVG renderer
 */
(function() {
    var svg = $.extend(function (name, attr, params) {
                var elems = [],
                    elem = svg.new_element(name, attr);
                if (elem) {
                    elems.push(elem);
                }
                return svgElement(elems, params);
            }, {
            svgNS: 'http://www.w3.org/2000/svg',
            version: '1.1',
            default_attributes: {
                'stroke-width': 1,
                'stroke-linejoin': "round",
                stroke: '#000',
                fill: 'none'
            },
            elements: {
                svg: {container: true},
                g: {container: true},
                rect: {container: false},
                circle: {container: false},
                ellipse: {container: false},
                line: {container: false},
                polygon: {container: false, attr: 'points'},
                polyline: {container: false, attr: 'points'},
                path: {container: false, attr: 'd'},
                text: {container: true}
            },
            new_element: function (name, attr) {
                var elem;
                if(name && typeof(name) !== 'string') {
                    elem = name;
                } else if (name && svg.elements[name] !== undefined) {
                    elem = document.createElementNS(this.svgNS, name);
                }
                if (elem !== undefined) {
                    this.attr(elem, attr);
                }
                return elem;
            },
            fill: function (self, color) {
                return this.attr(self, {fill: color});
            },
            stroke: function (self, color) {
                return this.attr(self, {stroke: color});
            },
            can_append: function (node) {
                var n = this.elements[node];
                return n ? n.container : false;
            },
            append: function (self, child) {
                if (this.can_append(self.nodeName)) {
                    if (child.nodeName !== undefined) {
                        self.appendChild(child);
                    } else {
                        for (var i = 0; i < child.length; i++) {
                            self.appendChild(child[i]);
                        }
                    }
                }
                return this;
            },
            draw: function (self, data) {
                $.each(data, function () {
                    var node = this.type,
                        data = this[node],
                        elem = svg.elements[node];
                    delete this.type;
                    if (data && elem.attr) {
                        delete this[node];
                        this[elem.attr] = data;
                    }
                    var child = svg.new_element(node, this);
                    self.appendChild(child);
                });
            },
            find: function (self, selector) {
                var elem = svgElement(),
                    target = $(self).find(selector);
                for (var j = 0; j < target.length; j++) {
                    elem.push(target[j]);
                }
                return elem;
            },
            attr: function (self, attrs, value) {
                if (typeof(attrs) === 'string') {
                    if (value === undefined) {
                        return self.getAttribute(attrs);
                    } else {
                        var a = {};
                        a[attrs] = value;
                        attrs = a;
                    }
                }
                if (attrs) {
                    $.each(attrs, function (name, value) {
                        if (value !== null && value !== undefined && value !== '') {
                            value += '';
                            self.setAttribute(name, value);
                        }
                    });
                }
            },
            viewbox: function (self, value) {
                var val = this.attr(self, 'viewBox', value);
                if (val !== this) {
                    val = val.split(' ');
                    return $.extend(val, {
                        minx: val[0],
                        miny: val[1],
                        width: val[2],
                        height: val[3]
                    });
                }
            },
            matrix: function (self, value) {
                if (value === undefined) {
                    value = self.getAttribute('transform');
                    if (value) {
                    } else {
                        return lux .utils.matrix3([1,0,0,0,1,0,0,0,1]);
                    }
                } else {
                    
                }
            },
            translate: function (self, x, y) {
                var matrix = this.matrix(self);
                self.translate(x, y);
            },
            rotate: function (self, radian) {
                var matrix = this.matrix(self);
                self.rotate(radian);
            }
        });
    $.lux.svg = svg;
    //
    // Create a new svg element
    function svgElement(elems, params) {
        params = params || {};
        elems = $.isArray(elems) ? elems : []; 
        return $.extend(elems, {
            parameters: function (pars) {
                if(pars === undefined) {
                    return params;
                } else {
                    params = pars || {};
                }
            },
            each: function (callback) {
                for (var i = 0; i < this.length; i++) {
                    callback.call(this[i], i);
                }
                return this;
            },
            // set attributes to elements
            attr: function (attrs, value) {
                if (typeof(attrs) === 'string' && value === undefined) {
                    if(this.length === 1) {
                        return svg.attr(this[0], attrs);
                    } else {
                        var result = [];
                        this.each(function () {
                            result.push(svg.attr(this, attrs));
                        });
                        return result;
                    }
                }
                return this.each(function () {
                    svg.attr(this, attrs, value);
                });
            },
            append: function (element) {
                return this.each(function () {
                    svg.append(this, element);
                });
            },
            children: function () {
                var elements = svgElement();
                this.each(function () {
                    for (var j = 0; j < this.childNodes.length; j++) {
                        elements.push(this.childNodes[j]);
                    }
                });
                return elements;
            },
            child: function (name, attr) {
                var p = this.parameters();
                if (p && attr) {
                    p = $.extend({}, p, attr);
                } else if (!p) {
                    p = attr;
                }
                var elem = svg.new_element(name, p);
                this.append(elem);
                return svg.svg(elem);
            },
            set: function () {
                return this.child('g');
            },
            line: function (x1, y1, x2, y2) {
                return this.child('line', {'x1': x1 || 0, 'y1': y1 || 0, 'x2': x2 || 0, 'y2': y2 || 0});
            },
            polyline: function (points, step) {
                var str = [];
                step = step || 2;
                for (var i = 0; i < points.length; i += step) {
                    var x = points[i],
                        y = points[i + 1];
                    if (x === null || y === null) {
                        continue;
                    }
                    str.push(x + ',' + y);
                }
                return this.child('polyline', {points: str.join(' ')});
            },
            circle: function (x, y, r) {
                return this.child('circle', {cx: x || 0, cy: y || 0, 'r': r || 0});
            },
            ellipse: function (x, y, rx, ry) {
                return this.child('ellipse', {cx: x, cy: y, 'rx': rx, 'ry': ry});
            },
            rect: function (x, y, w, h, r) {
                return this.child('rect', {'x': x || 0, 'y': y || 0, width: w || 0,
                                                height: h || 0, rx: r || 0, ry: r || 0});
            },
            fill: function (color) {
                return this.attr({fill: color});
            },
            stroke: function (color) {
                return this.attr({stroke: color});
            },
            lineWidth: function (width) {
                return this.attr({'stroke-width': width});
            },
            lineJoin: function (value) {
                return this.attr({'stroke-linejoin': value});
            },
            viewbox: function (value) {
                return this.attr({'viewBox': value});
            },
            translate: function (x, y) {
                return this.each(function () {
                    svg.translate(this, x, y);
                });
            },
            rotate: function (radian) {
                return this.each(function () {
                    svg.rotate(this, radian);
                });
            },
            find: function (selector) {
                if (this.length === 1) {
                    return svg.find(this[0], selector);
                } else {
                    var elements = svgElement();
                    this.each(function () {
                        var elems = svg.find(this, selector);
                        for (var j = 0; j < elems.length; j++) {
                            elements.push(elems[j]);
                        }
                    });
                    return elements;
                }
            },
            event: function (name, handler1, handler2) {
                return this.each(function () {
                    if(handler2) {
                        $(this)[name](function (e) {
                            e.target = svg.svg(e.target);
                            handler1(e);
                        },
                        function (e) {
                            e.target = svg.svg(e.target);
                            handler2(e);
                        });
                    } else {
                        $(this)[name](function (e) {
                            e.target = svg.svg(e.target);
                            handler1(e);
                        });
                    }
                });
            },
            hover: function (handler_in, handler_out) {
                return this.event('hover', handler_in, handler_out);
            },
            draw: function (data) {
                return this.each(function () {
                    svg.draw(this, data);
                });
            }
        });
    }
    //
    lux.paper.add_paper_type('svg', {
        init: function () {
            var s = svg('svg',
                        {xmlns: svg.svgNS, version: svg.version},
                        svg.default_attributes);
            $.extend(s, this);
            s.container().append(s[0]);
            return s.resize(s.container());
        },
        resize: function (placeholder) {
            var canvasWidth = placeholder.width(),
                canvasHeight = placeholder.height();
            return this.attr({height: canvasHeight, width: canvasWidth});
        }
    });
}());