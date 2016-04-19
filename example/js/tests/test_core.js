define(['lux/main'], function (lux) {
    'use strict';

    describe('Test lux utilities', function () {

        it('Check lux object', function () {
            expect(lux).not.toBe(undefined);
            expect(typeof(lux.version)).toBe('string');
            expect(lux.version.split('.').length).toBe(3);
        });

        it('Check lux urls', function () {
            expect(lux.context.url).toBe('');
        });

        it('Check lux media function', function () {
            var ctx = {MEDIA_URL: '/mediax/'};
            expect(lux.media('foo', ctx)).toBe('/mediax/foo');
            expect(lux.media('/foo', ctx)).toBe('/mediax/foo');
            expect(lux.media('////foo', ctx)).toBe('/mediax/foo');
            expect(lux.media('//foo/////', ctx)).toBe('/mediax/foo/');
        });

        var joinUrl = lux.joinUrl;

        it('Check joinUrl', function () {
            expect(joinUrl('bla', 'foo')).toBe('bla/foo');
            expect(joinUrl('bla/', '/foo')).toBe('bla/foo');
            expect(joinUrl('bla', '')).toBe('bla');
            expect(joinUrl('bla', '///foo')).toBe('bla/foo');
            expect(joinUrl('bla//////', '///foo')).toBe('bla/foo');
        });

        it('Test addEvent', function () {
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

        it('Test extendArray', function () {
            var extendArray = lux.extendArray;

            expect(extendArray()).toBe(undefined);
            expect(extendArray(1)).toBe(1);
            var a = ['bla'];
            expect(extendArray(a, ['foo', 4])).toBe(a);
            expect(a.length).toBe(3);
            expect(a[0]).toBe('bla');
            expect(a[1]).toBe('foo');
            expect(a[2]).toBe(4);
            a = [];
            expect(extendArray(a, ['foo', 4], null, ['pippo', 'j'])).toBe(a);
            expect(a.length).toBe(4);

        });

        it('Test getOptions', function () {
            var a = [];
            lux.testing = {'v': a};
            expect(lux.getOptions({options: 'lux.testing.v', b: 4})).toBe(a);
            a = 'ciao';
            lux.testing.v = a;
            expect(lux.getOptions({options: 'lux.testing.v', b: 4})).toBe(a);
            a = {};
            lux.testing.v = a;
            expect(lux.getOptions({options: 'lux.testing.v', b: 4}).b).toBe(4);
        });

        it('Test querySelector', function () {
            var body = lux.querySelector(document);
            expect(body.length).toBe(1);
            expect(body[0]).toBe(document);

            body = lux.querySelector('body');
            expect(body.length).toBe(1);
            expect(body[0].tagName).toBe('BODY');
        });

        it('Check getJsonOrNone', function () {
            var res;
            res = lux.getJsonOrNone('{"id": 1}');
            expect(res.id).toBe(1);
            res = lux.getJsonOrNone('{id: 1}');
            expect(res).toBe(null);
        });

        it('Check isJsonStringify', function () {
            var res;
            res = lux.isJsonStringify('[123, 234]');
            expect(res).toBe(true);
            res = lux.isJsonStringify('{id: 1}');
            expect(res).toBe(true);
            res = lux.isJsonStringify('value');
            expect(res).toBe(true);
        });
    });

});
