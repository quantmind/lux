import {module, compile, newScope, httpBackend, _} from './tools';
import '../index';


describe('lux core', function() {

    _.module('lux.grid.test', ['lux.grid', 'lux.mocks'])
        .run(($lux) => {
            $lux.$require = function (deps, callback) {
                callback();
            };
        });

    beforeEach(() => {
        module('lux.grid.test');
    });

    it('Test grid', (done) => {
        var scope = newScope();
        scope.testOptions = {
            target: '/api/users',
            onRegisterApi: function () {
                done();
            }
        };

        var element = compile(`<div><lux-grid grid-options="testOptions"></lux-grid></div>`, scope),
            grid = element.children(),
            gridScope = grid.isolateScope(),
            $httpBackend = httpBackend();

        expect(grid.length).toBe(1);
        expect(gridScope.$parent).toBe(scope);
        $httpBackend.flush(1);
        // TODO: fix this test
        done();
    });

});
