define(['lux',
        'lux/google'], function (lux) {
    'use strict';

    describe('Test google spreadsheet api', function () {
        var $lux = angular.injector(['lux.mocks.lux']).get('$lux');
        //
        it('contains spec with an expectation', function () {
            var api = $lux.api({
                name: 'googlesheets',
                url: '19_Sy0WAiwvvfDXBxrbWtXHEYhgI44RPnrLlUUJMOImE'
            });
            expect(api instanceof lux.ApiClient).toBe(true);
            expect(api.name).toBe('googlesheets');
            expect(api._url).toBe('19_Sy0WAiwvvfDXBxrbWtXHEYhgI44RPnrLlUUJMOImE');
        });
    });

});
