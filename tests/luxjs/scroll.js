    describe("Test lux.scroll module", function() {
        var scope;

        beforeEach(function () {
            module('lux.scroll');
        });

        it("Scroll scope", function() {
            //
            scope = $rootScope.$new();

            afterEach(function () {
                scope.$digest();
            });

            it("root scope defaults", function() {
                expect(typeof(scope.scroll)).toBe('object');
                expect(scope.scroll.time).toBe(1);
                expect(scope.scroll.offset).toBe(0);
                expect(scope.scroll.frames).toBe(25);
            });
        });
    });