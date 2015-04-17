
    describe("Test lux.restapi module", function() {
    	var context = {
    		API_URL: '/api'
    	};

        angular.module('lux.restapi.test', ['lux.loader', 'lux.restapi', 'lux.restapi.mock'])
        	.value('context', context);

        beforeEach(module('lux.restapi.test'));

        it("Luxrest api object", inject(['$rootScope', function (scope) {
            expect(_.isFunction(scope.api)).toBe(true);
            var client = scope.api();
            expect(_.isObject(client)).toBe(true);

            expect(client.baseUrl()).toBe('/api');
        }]));

    });
