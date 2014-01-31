(function() {
  var root;
  var __indexOf = Array.prototype.indexOf || function(item) {
    for (var i = 0, l = this.length; i < l; i++) {
      if (this[i] === item) return i;
    }
    return -1;
  };
  root = typeof exports !== "undefined" && exports !== null ? exports : this;
  root.jColour = (function() {
    var colourNames, hexify, hslToRgb, hueToRgb, minMax, properties, rgbToHsl, throwIfIncompatible;
    function jColour(col) {
      var h1, h2, h3, hex, hsl, rgb;
      if (col == null) {
        col = '#ffffff';
      }
      if (col.toLowerCase() in colourNames) {
        col = colourNames[col];
      }
      if (hex = col.match(/^#?([a-f0-9]{3})$/i)) {
        h1 = hex[1].substring(0, 1);
        h2 = hex[1].substring(1, 2);
        h3 = hex[1].substring(2, 3);
        col = "#" + (h1 + h1 + h2 + h2 + h3 + h3);
      }
      if (hex = col.match(/^#?([a-f0-9]{6,8})$/i)) {
        this.red = parseInt(hex[1].substring(0, 2), 16);
        this.green = parseInt(hex[1].substring(2, 4), 16);
        this.blue = parseInt(hex[1].substring(4, 6), 16);
        this.alpha = hex[1].substring(6, 8) ? parseInt(hex[1].substring(6, 8), 16) / 255 : 1;
        rgbToHsl(this);
      } else if (rgb = col.match(/^rgba?\(\s*(\d+)[,\s]*(\d+)[,\s]*(\d+)[,\s]*([\.\d]+)?\s*\)$/i)) {
        this.red = parseInt(rgb[1]);
        this.green = parseInt(rgb[2]);
        this.blue = parseInt(rgb[3]);
        this.alpha = rgb[4] ? rgb[4] : 1;
        rgbToHsl(this);
      } else if (hsl = col.match(/^hsla?\(\s*(\d+)[,\s]*(\d+)[,\s]*(\d+)[,\s]*([\.\d]+)?\s*\)$/i)) {
        this.hue = parseInt(hsl[1]);
        this.saturation = parseInt(hsl[2]);
        this.lightness = parseInt(hsl[3]);
        this.alpha = hsl[4] ? hsl[4] : 1;
        hslToRgb(this);
      } else {
        throw 'Invalid colour string.';
      }
    }
    jColour.prototype.hex = function(showAlpha) {
      var hex;
      if (showAlpha == null) {
        showAlpha = false;
      }
      hex = showAlpha && this.alpha < 1 ? "#" + (hexify(this.red)) + (hexify(this.green)) + (hexify(this.blue)) + (hexify(this.alpha * 255)) : "#" + (hexify(this.red)) + (hexify(this.green)) + (hexify(this.blue));
      return hex.toLowerCase();
    };
    jColour.prototype.rgb = function() {
      if (this.alpha === 1) {
        return "rgb(" + (Math.round(this.red)) + ", " + (Math.round(this.green)) + ", " + (Math.round(this.blue)) + ")";
      } else {
        return "rgba(" + (Math.round(this.red)) + ", " + (Math.round(this.green)) + ", " + (Math.round(this.blue)) + ", " + (Math.round(this.alpha * 100) / 100) + ")";
      }
    };
    jColour.prototype.hsl = function() {
      if (this.alpha === 1) {
        return "hsl(" + (Math.round(this.hue)) + ", " + (Math.round(this.saturation)) + ", " + (Math.round(this.lightness)) + ")";
      } else {
        return "hsla(" + (Math.round(this.hue)) + ", " + (Math.round(this.saturation)) + ", " + (Math.round(this.lightness)) + ", " + (Math.round(this.alpha * 100) / 100) + ")";
      }
    };
    jColour.prototype.toS = function() {
      var key, value;
      for (key in colourNames) {
        value = colourNames[key];
        if (this.hex() === value.toLowerCase()) {
          return key;
        }
      }
      return this.hex();
    };
    jColour.prototype.lighten = function(amount) {
      this.lightness += amount;
      return hslToRgb(this);
    };
    jColour.prototype.lightenPercent = function(percent) {
      this.lightness += (this.lightness / 100) * percent;
      return hslToRgb(this);
    };
    jColour.prototype.darken = function(amount) {
      this.lightness -= amount;
      return hslToRgb(this);
    };
    jColour.prototype.darkenPercent = function(percent) {
      this.lightness -= (this.lightness / 100) * percent;
      return hslToRgb(this);
    };
    jColour.prototype.saturate = function(amount) {
      this.saturation += amount;
      return hslToRgb(this);
    };
    jColour.prototype.saturatePercent = function(percent) {
      this.saturation += (this.saturation / 100) * percent;
      return hslToRgb(this);
    };
    jColour.prototype.desaturate = function(amount) {
      this.saturation -= amount;
      return hslToRgb(this);
    };
    jColour.prototype.desaturatePercent = function(percent) {
      this.saturation -= (this.saturation / 100) * percent;
      return hslToRgb(this);
    };
    jColour.prototype.greyscale = function() {
      this.saturation = 0;
      return hslToRgb(this);
    };
    jColour.prototype.grayscale = function() {
      return this.greyscale();
    };
    jColour.prototype.adjustHue = function(degrees) {
      this.hue += degrees;
      return hslToRgb(this);
    };
    jColour.prototype.complement = function() {
      this.hue += 180;
      return hslToRgb(this);
    };
    jColour.prototype.opacify = function(amount) {
      this.alpha += amount;
      this.alpha = minMax(this.alpha, 0, 1);
      return this;
    };
    jColour.prototype.transparentize = function(amount) {
      this.alpha -= amount;
      this.alpha = minMax(this.alpha, 0, 1);
      return this;
    };
    jColour.prototype.invert = function() {
      var color, _i, _len, _ref;
      _ref = ['red', 'green', 'blue'];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        color = _ref[_i];
        this[color] = 255 - this[color];
      }
      return rgbToHsl(this);
    };
    jColour.prototype.adjustColour = function(params) {
      var key, kind;
      if (params == null) {
        params = {};
      }
      kind = throwIfIncompatible(params);
      for (key in params) {
        if (__indexOf.call(properties, key) >= 0) {
          this[key] += params[key];
        }
      }
      if (kind[0]) {
        return rgbToHsl(this);
      } else {
        return hslToRgb(this);
      }
    };
    jColour.prototype.scaleColour = function(params) {
      var key, kind;
      if (params == null) {
        params = {};
      }
      kind = throwIfIncompatible(params);
      for (key in params) {
        if (__indexOf.call(properties, key) >= 0 && key !== 'hue') {
          this[key] += (this[key] / 100) * params[key];
        }
      }
      if (kind[0]) {
        return rgbToHsl(this);
      } else {
        return hslToRgb(this);
      }
    };
    jColour.prototype.changeColour = function(params) {
      var key, kind;
      if (params == null) {
        params = {};
      }
      kind = throwIfIncompatible(params);
      for (key in params) {
        if (__indexOf.call(properties, key) >= 0) {
          this[key] = params[key];
        }
      }
      if (kind[0]) {
        return rgbToHsl(this);
      } else {
        return hslToRgb(this);
      }
    };
    jColour.prototype.mixWith = function(colour, weight) {
      var a, p, w, w1, w2;
      if (weight == null) {
        weight = 50;
      }
      if (!(colour instanceof jColour)) {
        colour = new jColour(colour);
      }
      p = weight / 100;
      w = p * 2 - 1;
      a = colour.alpha - this.alpha;
      w1 = ((w * a === -1 ? w : (w + a) / (1 + w * a)) + 1) / 2;
      w2 = 1 - w1;
      this.red = (colour.red * w1) + (this.red * w2);
      this.green = (colour.green * w1) + (this.green * w2);
      this.blue = (colour.blue * w1) + (this.blue * w2);
      this.alpha = (colour.alpha * p) + (this.alpha * (1 - p));
      return rgbToHsl(this);
    };
    properties = ['red', 'green', 'blue', 'hue', 'saturation', 'lightness', 'alpha'];
    colourNames = {
      aliceblue: '#F0F8FF',
      antiquewhite: '#FAEBD7',
      aqua: '#00FFFF',
      aquamarine: '#7FFFD4',
      azure: '#F0FFFF',
      beige: '#F5F5DC',
      bisque: '#FFE4C4',
      black: '#000000',
      blanchedalmond: '#FFEBCD',
      blue: '#0000FF',
      blueviolet: '#8A2BE2',
      brown: '#A52A2A',
      burlywood: '#DEB887',
      cadetblue: '#5F9EA0',
      chartreuse: '#7FFF00',
      chocolate: '#D2691E',
      coral: '#FF7F50',
      cornflowerblue: '#6495ED',
      cornsilk: '#FFF8DC',
      crimson: '#DC143C',
      cyan: '#00FFFF',
      darkblue: '#00008B',
      darkcyan: '#008B8B',
      darkgoldenrod: '#B8860B',
      darkgray: '#A9A9A9',
      darkgreen: '#006400',
      darkgrey: '#A9A9A9',
      darkkhaki: '#BDB76B',
      darkmagenta: '#8B008B',
      darkolivegreen: '#556B2F',
      darkorange: '#FF8C00',
      darkorchid: '#9932CC',
      darkred: '#8B0000',
      darksalmon: '#E9967A',
      darkseagreen: '#8FBC8F',
      darkslateblue: '#483D8B',
      darkslategray: '#2F4F4F',
      darkslategrey: '#2F4F4F',
      darkturquoise: '#00CED1',
      darkviolet: '#9400D3',
      deeppink: '#FF1493',
      deepskyblue: '#00BFFF',
      dimgray: '#696969',
      dimgrey: '#696969',
      dodgerblue: '#1E90FF',
      firebrick: '#B22222',
      floralwhite: '#FFFAF0',
      forestgreen: '#228B22',
      fuchsia: '#FF00FF',
      gainsboro: '#DCDCDC',
      ghostwhite: '#F8F8FF',
      gold: '#FFD700',
      goldenrod: '#DAA520',
      gray: '#808080',
      green: '#008000',
      greenyellow: '#ADFF2F',
      grey: '#808080',
      honeydew: '#F0FFF0',
      hotpink: '#FF69B4',
      indianred: '#CD5C5C',
      indigo: '#4B0082',
      ivory: '#FFFFF0',
      khaki: '#F0E68C',
      lavender: '#E6E6FA',
      lavenderblush: '#FFF0F5',
      lawngreen: '#7CFC00',
      lemonchiffon: '#FFFACD',
      lightblue: '#ADD8E6',
      lightcoral: '#F08080',
      lightcyan: '#E0FFFF',
      lightgoldenrodyellow: '#FAFAD2',
      lightgray: '#D3D3D3',
      lightgreen: '#90EE90',
      lightgrey: '#D3D3D3',
      lightpink: '#FFB6C1',
      lightsalmon: '#FFA07A',
      lightseagreen: '#20B2AA',
      lightskyblue: '#87CEFA',
      lightslategray: '#778899',
      lightslategrey: '#778899',
      lightsteelblue: '#B0C4DE',
      lightyellow: '#FFFFE0',
      lime: '#00FF00',
      limegreen: '#32CD32',
      linen: '#FAF0E6',
      magenta: '#FF00FF',
      maroon: '#800000',
      mediumaquamarine: '#66CDAA',
      mediumblue: '#0000CD',
      mediumorchid: '#BA55D3',
      mediumpurple: '#9370DB',
      mediumseagreen: '#3CB371',
      mediumslateblue: '#7B68EE',
      mediumspringgreen: '#00FA9A',
      mediumturquoise: '#48D1CC',
      mediumvioletred: '#C71585',
      midnightblue: '#191970',
      mintcream: '#F5FFFA',
      mistyrose: '#FFE4E1',
      moccasin: '#FFE4B5',
      navajowhite: '#FFDEAD',
      navy: '#000080',
      oldlace: '#FDF5E6',
      olive: '#808000',
      olivedrab: '#6B8E23',
      orange: '#FFA500',
      orangered: '#FF4500',
      orchid: '#DA70D6',
      palegoldenrod: '#EEE8AA',
      palegreen: '#98FB98',
      paleturquoise: '#AFEEEE',
      palevioletred: '#DB7093',
      papayawhip: '#FFEFD5',
      peachpuff: '#FFDAB9',
      peru: '#CD853F',
      pink: '#FFC0CB',
      plum: '#DDA0DD',
      powderblue: '#B0E0E6',
      purple: '#800080',
      red: '#FF0000',
      rosybrown: '#BC8F8F',
      royalblue: '#4169E1',
      saddlebrown: '#8B4513',
      salmon: '#FA8072',
      sandybrown: '#F4A460',
      seagreen: '#2E8B57',
      seashell: '#FFF5EE',
      sienna: '#A0522D',
      silver: '#C0C0C0',
      skyblue: '#87CEEB',
      slateblue: '#6A5ACD',
      slategray: '#708090',
      slategrey: '#708090',
      snow: '#FFFAFA',
      springgreen: '#00FF7F',
      steelblue: '#4682B4',
      tan: '#D2B48C',
      teal: '#008080',
      thistle: '#D8BFD8',
      tomato: '#FF6347',
      turquoise: '#40E0D0',
      violet: '#EE82EE',
      wheat: '#F5DEB3',
      white: '#FFFFFF',
      whitesmoke: '#F5F5F5',
      yellow: '#FFFF00',
      yellowgreen: '#9ACD32'
    };
    rgbToHsl = function(c) {
      var b, d, g, h, l, max, min, r, s;
      c.red = minMax(c.red, 0, 255);
      c.green = minMax(c.green, 0, 255);
      c.blue = minMax(c.blue, 0, 255);
      c.alpha = minMax(c.alpha, 0, 1);
      r = c.red / 255;
      g = c.green / 255;
      b = c.blue / 255;
      max = Math.max(r, g, b);
      min = Math.min(r, g, b);
      d = max - min;
      h = (function() {
        switch (max) {
          case min:
            return 0;
          case r:
            return 60 * (g - b) / d;
          case g:
            return 60 * (b - r) / d + 120;
          case b:
            return 60 * (r - g) / d + 240;
        }
      })();
      l = (max + min) / 2;
      s = max === min ? 0 : l < 0.5 ? d / (2 * l) : d / (2 - 2 * l);
      c.hue = h % 360;
      c.saturation = s * 100;
      c.lightness = l * 100;
      return c;
    };
    hslToRgb = function(c) {
      var b, g, h, l, m1, m2, r, s;
      if (c.hue >= 360) {
        c.hue -= Math.floor(c.hue / 360) * 360;
      }
      if (c.hue < 0) {
        c.hue -= Math.ceil(c.hue / 360) * 360;
      }
      c.saturation = minMax(c.saturation, 0, 100);
      c.lightness = minMax(c.lightness, 0, 100);
      c.alpha = minMax(c.alpha, 0, 1);
      h = c.hue / 360;
      s = c.saturation / 100;
      l = c.lightness / 100;
      m2 = l < 0.5 ? l * (s + 1) : l + s - (l * s);
      m1 = l * 2 - m2;
      r = hueToRgb(m1, m2, h + 1 / 3);
      g = hueToRgb(m1, m2, h);
      b = hueToRgb(m1, m2, h - 1 / 3);
      c.red = r * 255;
      c.green = g * 255;
      c.blue = b * 255;
      return c;
    };
    hueToRgb = function(m1, m2, h) {
      if (h < 0) {
        h += 1;
      }
      if (h > 1) {
        h -= 1;
      }
      if (h * 6 < 1) {
        return m1 + (m2 - m1) * h * 6;
      }
      if (h * 2 < 1) {
        return m2;
      }
      if (h * 3 < 2) {
        return m1 + (m2 - m1) * (2 / 3 - h) * 6;
      }
      return m1;
    };
    hexify = function(n) {
      if (n == null) {
        n = '00';
      }
      n = parseInt(n);
      if (n === 0 || isNaN(n)) {
        return '00';
      }
      n = Math.round(minMax(n, 0, 255));
      return "0123456789ABCDEF".charAt((n - n % 16) / 16) + "0123456789ABCDEF".charAt(n % 16);
    };
    minMax = function(i, min, max) {
      return Math.min(Math.max(i, min), max);
    };
    throwIfIncompatible = function(params) {
      var hsl, key, rgb;
      rgb = hsl = false;
      for (key in params) {
        if (key === 'red' || key === 'green' || key === 'blue') {
          rgb = true;
        }
        if (key === 'hue' || key === 'saturation' || key === 'luminosity') {
          hsl = true;
        }
      }
      if (rgb && hsl) {
        throw 'Cannot change both RGB and HSL properties.';
      }
      return [rgb, hsl];
    };
    return jColour;
  })();
}).call(this);
