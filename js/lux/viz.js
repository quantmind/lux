    //
    //  Lux Vizualization Factory
    //  -------------------------------
    lux.Viz = function (element, attrs, build) {
        //
        element = $(element);
        //
        var self = this,
            parent = element.parent(),
            elwidth, elheight;

        if (!attrs.width) {
            attrs.width = element.width();
            if (attrs.width)
                elwidth = element;
            else {
                attrs.width = parent.width();
                if (attrs.width)
                    elwidth = parent;
                else
                    attrs.width = 400;
            }
        }
        //
        if (!attrs.height) {
            attrs.height = element.height();
            if (attrs.height)
                elheight = element;
            else {
                attrs.height = parent.height();
                if (attrs.height)
                    elheight = parent;
                else
                    attrs.height = 400;
            }
        }
        //
        this.element = element;
        this.attrs = attrs;

        //
        // Resize the vizualization
        this.resize = function () {
            var w = elwidth ? elwidth.width() : attrs.width,
                h = elheight ? elheight.height() : attrs.height;
            if (attrs.width !== w || attrs.height !== h) {
                attrs.width = w;
                attrs.height = h;
                build(self);
            }
        };

        this.svg = function (d3) {
            element.empty();
            return d3.select(element[0]).append("svg")
                .attr("width", attrs.width)
                .attr("height", attrs.height);
        };

        this.size = function () {
            return [attrs.width, attrs.height];
        };

        build(self);

        if (attrs.resize)
            $(window).resize(self.resize);
    };
