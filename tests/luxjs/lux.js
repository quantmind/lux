
    describe("Test lux angular app", function() {

        it("Check lux object", function() {
            expect(lux).not.toBe(undefined);
            expect(typeof(lux.version)).toBe('string');
            expect(lux.version.split('.').length).toBe(3);
        });

        it("Check lux urls", function() {
            expect(lux.context.url).toBe('');
            expect(lux.context.media).toBe('');
        });

        it("Check lux media function", function() {
            lux.context.media = '/media/'
            expect(lux.media('foo')).toBe('/media/foo');
            expect(lux.media('/foo')).toBe('/media/foo');
            expect(lux.media('////foo')).toBe('/media/foo');
            expect(lux.media('//foo/////')).toBe('/media/foo/');
        });
    });


    describe("Test utilis", function() {
        var joinUrl = lux.joinUrl;

        it("Check joinUrl", function() {
            expect(joinUrl('bla', 'foo')).toBe('bla/foo');
            expect(joinUrl('bla/', '/foo')).toBe('bla/foo');
            expect(joinUrl('bla', '')).toBe('bla');
            expect(joinUrl('bla', '///foo')).toBe('bla/foo');
            expect(joinUrl('bla//////', '///foo')).toBe('bla/foo');
        });

        it("Test addEvent", function() {
            expect(typeof(lux.addEvent)).toBe('function');
            var el = {},
                slice = Array.prototype.slice,
                c,
                callback = function () {
                    c = {caller: this, args: slice.call(arguments, 0)};
                };
            lux.addEvent(el, 'onwhatever', callback);
            expect(typeof(el.onwhatever)).toBe('function');
            expect(typeof(el.onwhatever.add)).toBe('function');
            el.onwhatever('ciao', 'luca');
            expect(c.caller).toBe(el);
            expect(c.args.length).toBe(2);
            expect(c.args[0]).toBe('ciao');
            expect(c.args[1]).toBe('luca');
        });
    });