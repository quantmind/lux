
    describe("Test lux angular app", function() {
        var $ = lux.$;

        it("Check $lux service", function() {
            var $injector = luxInjector();
            expect($injector.has('$lux')).toBe(true);
            var $lux = $injector.get('$lux');
            expect($lux).not.toBe(null);
            expect($lux.http).not.toBe(null);
            expect($lux.location).not.toBe(null);
            expect($lux.log).not.toBe(null);
            expect($.isFunction($lux.api)).toBe(true);
        });
    });
