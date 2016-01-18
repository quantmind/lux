define(['angular',
        'lux/services/pagination',
        'tests/mocks/rest'], function (angular) {
    'use strict';

    describe('Test lux.pagination module', function () {
        var LuxPagination;
        var $lux;

        // create a mock promise that returns data param
        function createMockPromise(data) {
            return {
                get: jasmine.createSpy().and.callFake(function () {
                    return {
                        then: function (callbacks) {
                            return callbacks(data);
                        }
                    };
                })
            };
        }

        beforeEach(function () {

            angular.mock.module('lux.pagination', function ($provide) {
                $provide.factory('$lux', function () {
                    var api = jasmine.createSpy('apiInit');
                    api.get = jasmine.createSpy('apiGet');
                    return {api: api};
                });
            });

            angular.mock.inject(function (_luxPaginationFactory_, _$lux_) {
                $lux = _$lux_;
                LuxPagination = _luxPaginationFactory_;
            });

        });

        afterEach(function () {
        });

        it('LuxPagination applies params to itself and set up API', inject(function () {
            var scope = 'scope';
            var target = {
                url: 'originalUrl'
            };
            var luxPag = new LuxPagination(scope, target);

            expect(luxPag.scope).toEqual(scope);
            expect(luxPag.target).toEqual(target);
            expect(luxPag.orgUrl).toEqual(target.url);
            expect($lux.api).toHaveBeenCalledWith(target);
            expect(luxPag.api).toEqual($lux.api(target));
        }));

        it('LuxPagination applies this.recursive only if parameter passed', function () {
            var recursive = true;
            var luxPag = new LuxPagination('target', 'scope', recursive);

            expect(luxPag.recursive).toBe(true);
            luxPag = new LuxPagination('target', 'scope');
            expect(luxPag.recursive).toBe(undefined);
        });

        it('LuxPagination.getData applies params to itself and calls API', function () {
            var params = 'params';
            var cb = jasmine.createSpy('callback');
            var mockData = {data: true};
            var luxPag = new LuxPagination('scope', 'target');

            // Fake promise returning good data
            luxPag.api = createMockPromise(mockData);
            LuxPagination.prototype.updateUrls = jasmine.createSpy('updateUrls');
            luxPag.getData(params, cb);
            expect(luxPag.params).toEqual(params);
            expect(luxPag.cb).toEqual(cb);
            expect(luxPag.api.get).toHaveBeenCalledWith(null, params);
            expect(luxPag.cb).toHaveBeenCalledWith(mockData);
            expect(luxPag.updateUrls).toHaveBeenCalledWith(mockData);
        });

        it('LuxPagination.updateUrls triggers emitEvent() and updates this.urls', function () {
            var data = {
                data: {
                    last: true,
                    next: true
                }
            };
            var luxPag = new LuxPagination('scope', 'target');

            LuxPagination.prototype.emitEvent = jasmine.createSpy('emittedEvent');
            luxPag.updateUrls(data);
            expect(luxPag.emitEvent).toHaveBeenCalled();
            expect(luxPag.urls).toEqual(data.data);
        });

        it('LuxPagination.updateUrls triggers loadMore() if this.recursive is true and data correct', function () {
            var recursive = true;
            var data = {
                data: {
                    last: true
                }
            };
            var luxPag = new LuxPagination('scope', 'target', recursive);

            LuxPagination.prototype.emitEvent = jasmine.createSpy('emittedEvent');
            LuxPagination.prototype.loadMore = jasmine.createSpy('loadingMore');
            luxPag.updateUrls(data);
            expect(luxPag.loadMore).toHaveBeenCalled();

        });

        it('LuxPagination.updateUrls wont do anything if data is incorrect', function () {
            var data = null;
            var luxPag = new LuxPagination('scope', 'target');

            LuxPagination.prototype.emitEvent = jasmine.createSpy('emittedEvent');
            LuxPagination.prototype.loadMore = jasmine.createSpy('loadingMore');
            luxPag.updateUrls(data);
            expect(luxPag.urls).toBe(undefined);
            expect(luxPag.loadMore).not.toHaveBeenCalled();
            expect(luxPag.emitEvent).not.toHaveBeenCalled();
        });

        it('LuxPagination.emitEvent emits event moreData on the provided scope', function () {
            var scope = {
                $emit: jasmine.createSpy('scopeEmit')
            };
            var luxPag = new LuxPagination(scope, 'target');
            luxPag.emitEvent();
            expect(scope.$emit).toHaveBeenCalledWith('moreData');
        });

        it('LuxPagination.loadMore updates this.target.url and calls getData', function () {
            var target = {url: 'url'};
            var luxPag = new LuxPagination('scope', target);

            LuxPagination.prototype.getData = jasmine.createSpy('getData');
            luxPag.urls = {
                next: 'next',
                last: 'last'
            };
            luxPag.loadMore();
            expect(luxPag.target.url).toEqual(luxPag.urls.next);
            expect(luxPag.getData).toHaveBeenCalled();
            luxPag.urls = {
                last: 'last',
                next: false
            };
            luxPag.loadMore();
            expect(luxPag.target.url).toEqual(luxPag.urls.last);
            expect(luxPag.getData).toHaveBeenCalled();
        });

        it('LuxPagination.search applies params to itself and calls getData', function () {
            var target = {url: 'originalUrl'};
            var query = 'query';
            var searchField = 'searchField';
            var luxPag = new LuxPagination('scope', target);

            LuxPagination.prototype.getData = jasmine.createSpy('getData');
            luxPag.params = undefined;
            luxPag.target.url = 'another url';
            luxPag.search(query, searchField);
            expect(luxPag.params).toEqual({searchField: query});
            expect(luxPag.target.url).toEqual(target.url);
            expect(luxPag.getData).toHaveBeenCalledWith({searchField: query});

            luxPag.params = {params: 'initial'};
            luxPag.search(query, searchField);
            expect(luxPag.params).toEqual({
                params: 'initial',
                searchField: query
            });
            expect(luxPag.getData).toHaveBeenCalledWith({
                params: 'initial',
                searchField: query
            });

        });

    });

});
