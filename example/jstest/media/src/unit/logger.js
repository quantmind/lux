module('lux.utils.logger');

test("logger", function() {
    var Logger = lux.Logger;
    equal(typeof(Logger), 'function', 'Logger is a function');
    //
    var logger = new Logger();
    equal(logger.handlers.length, 0, 'No handlers');
    // Create a jquery element
    var hnd = new lux.HtmlLogHandler('<div/>');
    logger.addHandler({level: 'warning'}, hnd);
    equal(logger.handlers.length, 1, '1 handler');
    equal(logger.handlers[0], hnd, 'handler in handlers');
    //
    logger.debug('ciao');
    var inner = hnd.elem.html();
    equal(inner, '', 'HTML handler debug');
    //
    logger.warning('ciao');
    inner = hnd.elem.html();
    equal(inner, '<pre class="warning">warning: ciao</pre>', 'HTML handler warning');
    hnd.elem.empty();
    //
    logger.error('ciao');
    inner = hnd.elem.html();
    equal(inner, '<pre class="error">error: ciao</pre>', 'HTML handler error');
    hnd.elem.empty();
});
