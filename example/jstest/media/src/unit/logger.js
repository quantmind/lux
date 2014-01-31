module('lux.utils.logger');

test("logger", function() {
    var Logger = lux.utils.Logger;
    equal(typeof(Logger), 'function', 'Logger is a function');
    //
    var logger = new Logger();
    equal(logger.handlers.length, 0, 'No handlers');
    // Create a jquery element
    var elem = $('<div/>');
    var hnd = logger.addElement(elem);
    equal(logger.handlers.length, 1, '1 handler');
    equal(logger.handlers[0], hnd, 'handler in handlers');
    //
    logger.debug('ciao');
    var inner = elem.html();
    equal(inner, '', 'HTML handler debug');
    elem.empty();
    //
    logger.info('ciao');
    inner = elem.html();
    equal(inner, '<pre class="lux-logger info">info: ciao</pre>', 'HTML handler info');
    elem.empty();
    //
    logger.warning('ciao');
    inner = elem.html();
    equal(inner, '<pre class="lux-logger warning">warning: ciao</pre>', 'HTML handler warning');
    elem.empty();
    //
    logger.error('ciao');
    inner = elem.html();
    equal(inner, '<pre class="lux-logger error">error: ciao</pre>', 'HTML handler error');
    elem.empty();
});
