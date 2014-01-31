/**
 * Provides requestAnimationFrame in a cross browser way.
 */
window.requestAnimFrame = (function() {
    return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame ||
    function( /* function FrameRequestCallback */ callback, /* DOMElement Element */ element) {
        return window.setTimeout(callback, 1000 / 60);
    };
})();
/**
 * Provides cancelAnimationFrame in a cross browser way.
 */
window.cancelAnimFrame = (function() {
    return window.cancelAnimationFrame || window.webkitCancelAnimationFrame || window.mozCancelAnimationFrame || window.oCancelAnimationFrame || window.msCancelAnimationFrame || window.clearTimeout;
})();
//
/**
 * General WebGL utilities
 */
var webgl = (function (w) {
    var webgl_names = ["webgl", "experimental-webgl", "webkit-3d", "moz-webgl"];
    $.lux.webgl = w;
    //
    function create3DContext (canvas, opt_attribs) {
        var context = null;
        for (var i = 0; i < webgl_names.length; i++) {
            var name = webgl_names[i];
            try {
                context = canvas.getContext(name, opt_attribs);
            } catch (e) {}
            if (context) {
                break;
            }
        }
        return context;
    }
    //
    return $.extend(w, {
        init: function (canvas, opt_attribs) {
            if (!window.WebGLRenderingContext) {
                return null;
            }
            var context = create3DContext(canvas, opt_attribs);
            if (!context) {
                return null;
            }
            return context;
        }
    });
}({}));
/**
 * Web GL shaders
 * 
 * WebGL makes it possible to display amazing realtime 3D graphics in your browser but
 * it is actually a 2D API, not a 3D API. WebGL only cares about 2 things:
 * clipspace coordinates in 2D and colors.
 * Your job as a programmer using WebGL is to provide WebGL with those 2 things.
 * You provide 2 "shaders" to do this. A Vertex shader which provides the clipspace
 * coordinates and a fragment shader that provides the color.
 */
webgl.shaders = (function () {
    function b() {
        var args = Array.prototype.slice.call(arguments);
        return args.join('\n');
    }
    var main = 'void main() {',
        eif = "#endif",
        ifmap = "#if defined( USE_MAP ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( USE_SPECULARMAP )",
        map_vertex = b(ifmap, "vUv = uv * offsetRepeat.zw + offsetRepeat.xy;", eif),
        map_pars_vertex = b(ifmap, "varying vec2 vUv;", "uniform vec4 offsetRepeat;", eif),
        map_pars_fragment = b(ifmap, "varying vec2 vUv;", eif, '#ifdef USE_MAP', "uniform sampler2D map;", eif);
    //
    return {
        '2d': {
            vertex: b('attribute vec2 a_position',
                      'uniform vec2 u_resolution;',
                      main,
                      // convert the rectangle from pixels to -1.0 to 1.0
                      'vec2 clipSpace = 2.0 * a_position / u_resolution - 1.0;',
                      'gl_Position = vec4(clipSpace, 0, 1);',
                      '}'),
            fragment: b(main, 'gl_Position = vec4(a_position, 0, 1);', '}')
        },
        basic: {
            vertex: b('void main() {', map_vertex, '}'),
            fragment: b('void main() {', '}')
        }
    };
});
/**
 * Web GL canvas
 */
lux.add_paper_type('webgl', {
    init: function (renderer) {
        var self = this,
            container = renderer.container(),
            c = document.createElement('canvas'),
            ctx = webgl.init(c);
        $(c).appendTo(container);
        $.extend(self, {
            canvas: function() {
                return c;
            },
            getContext: function() {
                return ctx;
            }
        });
        self.resize(container);
    },
    resize: function (placeholder) {
        var self = this,
            canvas = self.canvas(),
            ctx = self.getContext(),
            canvasWidth = placeholder.width(),
            canvasHeight = placeholder.height(),
            pixelRatio = getPixelRatio(ctx);
        //
        canvas.width = canvasWidth * pixelRatio;
        canvas.height = canvasHeight * pixelRatio;
        canvas.style.width = canvasWidth + "px";
        canvas.style.height = canvasHeight + "px";
        ctx.viewport(0, 0, canvas.width, canvas.height);
    },
    rect: function (x, y, w, h, r) {
    },
    loadShader: function (type, script) {
        var ctx = this.getContext(),
            shader,
            error,
            shaderType,
            compiled; 
        if (type == 'vertex') {
            shaderType = ctx.VERTEX_SHADER;
        } else if (type == 'fragment') {
            shaderType = ctx.FRAGMENT_SHADER;
        } else {
            return null;
        }
        shader = ctx.createShader(shaderType);
        // Load the shader source
        ctx.shaderSource(shader, script);
        // Compile the shader
        ctx.compileShader(shader);
        // Check the compile status
        compiled = ctx.getShaderParameter(shader, ctx.COMPILE_STATUS);
        if (!compiled && !ctx.isContextLost()) {
            // Something went wrong during compilation; get the error
            error = ctx.getShaderInfoLog(shader);
            logger.error("*** Error compiling shader '" + type + "':" + error);
            ctx.deleteShader(shader);
            return null;
        }
        return shader;
    }
});