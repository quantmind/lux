define(['angular',
        'lux/main',
        'lux/testing/main',
        'lux/forms/main'], function (angular) {
    'use strict';

    describe('Test lux.form.utils module', function () {
        var luxPagination;
        var scope;
        var compile;

        function getCompiledElem(markup) {
            var element = angular.element(markup);

            // test data
            scope.formModelName = 'UserForm';
            scope[scope.formModelName] = {groups: []};

            var compiled = compile(element)(scope);

            scope.$digest();
            return compiled;
        }

        beforeEach(function () {

            angular.mock.module('lux.form.utils', function ($provide) {

                $provide.factory('luxPagination', function () {
                    luxPagination = jasmine.createSpy('luxPag').and.callThrough();
                    luxPagination.prototype.getData = jasmine.createSpy('luxPagGetData');
                    luxPagination.prototype.loadMore = jasmine.createSpy('luxPagLoadMore');
                    luxPagination.prototype.search = jasmine.createSpy('luxPagSearch');
                    return luxPagination;
                });

            });

            angular.mock.inject(function (_$compile_, _$rootScope_, _luxPagination_) {
                luxPagination = _luxPagination_;
                scope = _$rootScope_.$new();
                compile = _$compile_;
            });

        });

        afterEach(function () {
        });

        it('remote options are parsed and an instance of luxPagination is created and the getData method is called', function () {
            var remoteOptions = '{"url": "http://127.0.0.1:6050", "name": "groups_url"}';
            var markup = '<div data-remote-options=\'' + remoteOptions + '\' data-remote-options-id="" name="groups[]"><input type="text"></input></div>';
            var params = {sortby: 'id:asc'};

            spyOn(angular, 'fromJson').and.callThrough();
            getCompiledElem(markup);

            expect(angular.fromJson).toHaveBeenCalled();
            expect(luxPagination).toHaveBeenCalledWith(scope, angular.fromJson(remoteOptions), false);
            expect(luxPagination.prototype.getData).toHaveBeenCalledWith(params, jasmine.any(Function));
        });

        it('if multiple attr is present instance of LuxPag is recursive and getData called with raised limit', function () {
            var remoteOptions = '{"url": "http://127.0.0.1:6050", "name": "groups_url"}';
            var markup = '<div multiple="multiple" data-remote-options=\'' + remoteOptions + '\' data-remote-options-id="" name="groups[]"><input type="text"></input></div>';
            var params = {limit: 200, sortby: 'id:asc'};
            getCompiledElem(markup);

            expect(luxPagination).toHaveBeenCalledWith(scope, angular.fromJson(remoteOptions), true);
            expect(luxPagination.prototype.getData).toHaveBeenCalledWith(params, jasmine.any(Function));
        });

        it('scope.$on is called when "more Data" event is emitted', function () {
            var markup = '<div data-remote-options=\'{"url": "http://127.0.0.1:6050", "name": "groups_url"}\' data-remote-options-id="" name="groups[]" multiple="multiple"><input type="text"></input></div>';

            spyOn(scope, '$on').and.callThrough();
            getCompiledElem(markup);
            scope.$emit('moreData');

            expect(scope.$on).toHaveBeenCalledWith('moreData', jasmine.any(Function));
        });

        it('enableSearch sets data("onKeyUp") to true and calls luxPag.search with event value', function () {
            var markup = '<div data-remote-options=\'{"url": "http://127.0.0.1:6050", "name": "groups_url"}\' data-remote-options-id="" name="groups[]" multiple="multiple"><input type="text"></input></div>';
            var elem = getCompiledElem(markup);
            var searchInput = angular.element(elem[0].querySelector('input[type=text]'));
            var mockEvent = {
                type: 'keyup',
                srcElement: {
                    value: 'longEnough'
                }
            };

            scope.$emit('moreData');
            expect(searchInput.data().onKeyUp).toBe(true);

            searchInput.triggerHandler(mockEvent);
            expect(luxPagination.prototype.search).toHaveBeenCalledWith(mockEvent.srcElement.value, jasmine.any(String));
        });

        it('enableSearch doesn\'t call luxPag.search if query is less than three chars', function () {
            var markup = '<div data-remote-options=\'{"url": "http://127.0.0.1:6050", "name": "groups_url"}\' data-remote-options-id="" name="groups[]" multiple="multiple"><input type="text"></input></div>';
            var elem = getCompiledElem(markup);
            var searchInput = angular.element(elem[0].querySelector('input[type=text]'));
            var mockEvent = {
                type: 'keyup',
                srcElement: {
                    value: 'not'
                }
            };

            scope.$emit('moreData');

            searchInput.triggerHandler(mockEvent);
            expect(luxPagination.prototype.search).not.toHaveBeenCalled();
        });

        it('enableSearch returns if data().onKeyUp is true', function () {
            var markup = '<div data-remote-options=\'{"url": "http://127.0.0.1:6050", "name": "groups_url"}\' data-remote-options-id="" name="groups[]" multiple="multiple"><input type="text"></input></div>';
            var elem = getCompiledElem(markup);
            var searchInput = angular.element(elem[0].querySelector('input[type=text]'));

            searchInput.data('onKeyUp', true);
            searchInput.on = jasmine.createSpy('searchInput.on');
            searchInput.data = jasmine.createSpy('searchInput.data');

            scope.$emit('moreData');
            searchInput.triggerHandler('keyup');

            expect(searchInput.on).not.toHaveBeenCalled();
            expect(searchInput.data).not.toHaveBeenCalled();
        });

        it('lazyLoad binds uiSelect to onscroll event and calls luxPag.loadMore if scroll offset reached', function () {
            var markup = '<div data-remote-options=\'{"url": "http://127.0.0.1:6050", "name": "groups_url"}\' data-remote-options-id="" name="groups[]" multiple="multiple"><input type="text"></input><ul class="ui-select-choices"><li class="ui-select-choices-group"></li></ul></div>';
            var elem = getCompiledElem(markup);
            var uiSelect = angular.element(elem[0].querySelector('.ui-select-choices'));

            scope.$emit('moreData');
            uiSelect.triggerHandler('scroll');

            expect(luxPagination.prototype.loadMore).toHaveBeenCalled();
        });

        it('buildSelect calls angular.forEach on data returned from luxPag.getData', function () {
            var remoteOptionsValue = '{"source": "name", "type": "field"}';
            var markup = '<div data-remote-options=\'{"url": "http://127.0.0.1:6050", "name": "groups_url"}\' data-remote-options-value=\'' + remoteOptionsValue + '\' data-remote-options-id="" name="groups[]" multiple="multiple"><input type="text"></input><ul class="ui-select-choices"><li class="ui-select-choices-group"></li></ul></div>';
            var fakeData = {
                data: {
                    result: [
                        {
                            name: 'bmll',
                            id: 1
                        },
                        {
                            name: 'moex',
                            id: 2
                        },
                        {
                            name: 'bmll',
                            id: 3
                        },
                        {
                            name: 'lol',
                            id: 4
                        }
                    ]
                }
            };

            luxPagination.prototype.getData = function (params, cb) {
                cb(fakeData);
            };
            spyOn(angular, 'forEach').and.callThrough();
            getCompiledElem(markup);

            expect(angular.forEach).toHaveBeenCalledWith(fakeData.data.result, jasmine.any(Function));
        });
    });

});
