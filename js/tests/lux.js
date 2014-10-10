
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
            expect(lux.media('foo')).toBe('/foo');
            expect(lux.media('/foo')).toBe('/foo');
            expect(lux.media('////foo')).toBe('/foo');
        });
    });
