    lux.web.visual_test('async', function () {
        var elem = $(document.createElement('div')).appendTo(this).width(100).height(100)
            .css({
                background: '#0F4FA8',
                position: 'relative',
                color: '#fff'
            });
        var coroutine = function (f) {
            var o = f(); // instantiate the coroutine
            o.send(); // execute until the first yield
            return function(x) {
                o.send(x);
            }
        };
        var loop = coroutine(function() {
            var e;
            while (e = yield) {
              if (e.type == 'mousedown') {
                while (e = yield) {
                  if (e.type == 'mousemove')
                    move(e);
                  if (e.type == 'mouseup')
                    break;
                }
              }
              // ignore mousemoves
            }
        });
        elem.mousedown(loop);
    });