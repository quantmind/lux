
    describe("Test lux angular app", function() {

        it("Check lux object", function() {
            expect(lux).not.toBe(undefined);
            expect(typeof(lux.version)).toBe('string');
            expect(lux.version.split('.').length).toBe(3);
        });
    });
