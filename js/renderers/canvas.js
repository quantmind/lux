//////////////////////////////////////////////////////////////////////////////////
// Returns the display's ratio between physical and device-independent pixels.
//
// This is the ratio between the width that the browser advertises and the number
// of pixels actually available in that space. The iPhone 4, for example, has a
// device-independent width of 320px, but its screen is actually 640px wide. It
// therefore has a pixel ratio of 2, while most normal devices have a ratio of 1.
function getPixelRatio(cctx) {
    if (window.devicePixelRatio > 1 &&
        (cctx.webkitBackingStorePixelRatio === undefined ||
         cctx.webkitBackingStorePixelRatio < 2)) {
        return window.devicePixelRatio;
    } else {
        return 1;
    }
}

lux.paper.add_paper_type('canvas', {
    init: function () {
        var self = this,
            c = document.createElement('canvas'),
            cctx;
        $(c).appendTo(self.container());
        if (!c.getContext) {// excanvas hack
            c = window.G_vmlCanvasManager.initElement(c);
        }
        cctx = c.getContext("2d");
        $.extend(self, {
            canvas: function() {
                return c;
            },
            context: function() {
                return cctx;
            }
        });
        self.resize(self.container());
        self.lineJoin('round');
        return self;
    },
    resize: function(placeholder) {
        var self = this,
            canvas = self.canvas(),
            cctx = self.context(),
            pixelRatio = getPixelRatio(cctx),
            canvasWidth = placeholder.width(),
            canvasHeight = placeholder.height();
        //
        canvas.width = canvasWidth * pixelRatio;
        canvas.height = canvasHeight * pixelRatio;
        canvas.style.width = canvasWidth + "px";
        canvas.style.height = canvasHeight + "px";
        // so try to get back to the initial state (even if it's
        // gone now, this should be safe according to the spec)
        cctx.restore();
        // and save again
        cctx.save();
        // Apply scaling for retina displays, as explained in makeCanvas
        cctx.scale(pixelRatio, pixelRatio);
    },
    setStart: function () {
        this.context().beginPath();
    },
    setFinish: function () {
        this.context().endPath();
    },
    line: function (x, y, x1, y1) {
        var ctx = this.context();
        ctx.moveTo(x, y);
        ctx.lineTo(x1, y1);
    },
    circle: function (x, y, r) {
        var ctx = this.context();
        ctx.moveTo(x+r, y);
        ctx.arc(x, y, r, 0, 2*PI);
    },
    ellipse: function (x, y, rx, ry) {
        var ctx = this.context(),
            scale;
        if (rx > 0 && ry > 0) {
            scale = ry/rx;
            ctx.save();
            ctx.moveTo(x+rx, y);
            ctx.scale(1, scale);
            ctx.arc(x, y/scale, rx, 0, 2*PI);
            ctx.restore();
        }
    },
    rect: function (x, y, w, h, r) {
        var ctx = this.context();
        if(r > 0) {
            if(2*r > w) {
                r = w/2;
            }
            ctx.moveTo(x+r, y);
            ctx.lineTo(x+w-r, y);
            ctx.arc(x+w-r, y+r, r, 3*Math.PI/2, 2*Math.PI);
            ctx.lineTo(x+w, y+h-r);
            ctx.arc(x+w-r, y+h-r, r, 0, Math.PI/2);
            ctx.lineTo(x+r, y+h);
            ctx.arc(x+r, y+h-r, r, Math.PI/2, Math.PI);
            ctx.lineTo(x, y+r);
            ctx.arc(x+r, y+r, r, Math.PI, 3*Math.PI/2);
        } else {
            ctx.rect(x, y, w, h);
        }
    },
    text: function (x, y, text) {
        var ctx = this.context();
        ctx.strokeText(text, x, y);
        return ctx;
    },
    polyline: function (points, step) {
        var pos = step,
            prevx = null,
            prevy = null,
            ctx = this.context();
        for (var i = step; i < points.length; i += step) {
            var x1 = points[i - step],
                y1 = points[i - step + 1],
                x2 = points[i],
                y2 = points[i + 1];
            if (x2 === null || y2 === null) {
                continue;
            }
            if (x1 != prevx || y1 != prevy) {
                ctx.moveTo(x1, y1);
            }
            prevx = x2;
            prevy = y2;
            ctx.lineTo(x2, y2);
        }
    },
    lineWidth: function (width) {
        var ctx = this.context();
        ctx.restore();
        ctx.lineWidth = width;
        ctx.save();
    },
    lineJoin: function (value) {
        if (value === 'none') {
            value = 'miter';
        }
        var ctx = this.context();
        ctx.restore();
        ctx.lineJoin = value;
        ctx.save();
    },
    clear: function () {
        this.context().beginPath();
    },
    fill: function (color) {
        var ctx = this.context();
        if (color === 'none') {
            color = null;
        }
        ctx.fillStyle = color;
        ctx.fill();
    },
    draw: function () {
        var ctx = this.context();
        ctx.stroke();
        ctx.beginPath();
    }
});
