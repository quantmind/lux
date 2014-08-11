
    describe("Test google spreadsheet api", function() {
        var $injector = luxInjector(),
            $httpBackend = $injector.get('$httpBackend'),
            $lux = $injector.get('$lux');

        $lux.http = function (options) {
            var d = $httpBackend.expect(options.method, options.url, options.data);
            d.success = function () {return this;};
            d.error = function () {return this;};
            return d;
        };

        beforeEach(function () {
            $httpBackend.when("GET").respond([{}, {}, {}]);
        });
        //
        it("contains spec with an expectation", function() {
            var api = $lux.api({
                name: 'googlesheets',
                url: '19_Sy0WAiwvvfDXBxrbWtXHEYhgI44RPnrLlUUJMOImE'
            });
            expect(api instanceof lux.ApiClient).toBe(true);
            expect(api.name).toBe('googlesheets');
            expect(api._url).toBe('19_Sy0WAiwvvfDXBxrbWtXHEYhgI44RPnrLlUUJMOImE');
            //
            var d = api.getMany();
        });
    });
