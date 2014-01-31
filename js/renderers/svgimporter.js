/*globals loadXML4IE*/
(function () {    
    function loadSVG (elem, dom) {
        $.each(dom.attributes, function () {
            var node = this.nodeName;
            if (!(node === 'version' || node.substring(0, 5) === 'xmlns')) {
                lux.svg.attr(elem, node, this.nodeValue);
            }
        });
        $.each(dom.childNodes, function () {
            var child = lux.svg.new_element(this.nodeName);
            if (child) {
                loadSVG(child, this);
                lux.svg.append(elem, child);
            }
        });
    }
    //
    lux.paper.renderers.svg.import_file = function (url, callback, errback) {
        var self = this;
        $.ajax({
            'url': url,
            dataType: ($.browser.msie ? 'text' : 'xml'),
            success: function (text) {
                var dom = $.browser.msie ? loadXML4IE(text) : text;
                if (!dom) {
                    return;
                }
                if (dom.documentElement.nodeName !== 'svg') {
                    logger.error('No svg node');
                    return;
                }
                loadSVG(self[0], dom.documentElement);
                if (callback) {
                    callback(self);
                }
            },
            error: function(http, message, exc) {
                logger.error(message + (exc ? ' ' + exc.message : ''));
                if (errback) {
                    errback(self);
                }
            }
        });
    };
}());