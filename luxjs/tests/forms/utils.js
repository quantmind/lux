describe('Test lux.form.utils module', function() {
    var LuxPagination;
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
    };

    beforeEach(function() {

        angular.mock.module('lux.form.utils', function($provide) {

            $provide.factory('luxPaginationFactory', function() {
                LuxPagination = jasmine.createSpy('luxPag').and.callThrough();
                LuxPagination.prototype.getData = jasmine.createSpy('luxPagGetData');
                LuxPagination.prototype.loadMore = jasmine.createSpy('luxPagLoadMore');
                LuxPagination.prototype.search = jasmine.createSpy('luxPagSearch');
                return LuxPagination;
            });

        });

        angular.mock.inject(function(_$compile_, _$rootScope_, _luxPaginationFactory_) {
            LuxPagination = _luxPaginationFactory_;
            scope = _$rootScope_.$new();
            compile = _$compile_;
        });

    });

    afterEach(function () {
    });

    it('remote options are parsed and an instance of LuxPagination is created and the getData method is called', function() {
        spyOn(JSON, 'parse').and.callThrough();
        var remoteOptions = '{"url": "http://127.0.0.1:6050", "name": "groups_url"}';
        var markup = '<div data-remote-options=\'' + remoteOptions + '\' data-remote-options-id="" name="groups[]"><input type="text"></input></div>';
        var elem = getCompiledElem(markup);

        expect(JSON.parse).toHaveBeenCalled();
        expect(LuxPagination).toHaveBeenCalledWith(scope, JSON.parse(remoteOptions), false);
        expect(LuxPagination.prototype.getData).toHaveBeenCalledWith({}, jasmine.any(Function));
    });

    it('if multiple attr is present instance of LuxPag is recursive and getData called with raised limit', function() {
        var remoteOptions = '{"url": "http://127.0.0.1:6050", "name": "groups_url"}';
        var markup = '<div multiple="multiple" data-remote-options=\'' + remoteOptions + '\' data-remote-options-id="" name="groups[]"><input type="text"></input></div>';
        var elem = getCompiledElem(markup);

        expect(LuxPagination).toHaveBeenCalledWith(scope, JSON.parse(remoteOptions), true);
        expect(LuxPagination.prototype.getData).toHaveBeenCalledWith({limit: 200}, jasmine.any(Function));
    });

    it('scope.$on is called when "more Data" event is emitted', function() {
        spyOn(scope, '$on').and.callThrough();
        var markup = '<div data-remote-options=\'{"url": "http://127.0.0.1:6050", "name": "groups_url"}\' data-remote-options-id="" name="groups[]" multiple="multiple"><input type="text"></input></div>';
        var elem = getCompiledElem(markup);

        scope.$emit('moreData');

        expect(scope.$on).toHaveBeenCalledWith('moreData', jasmine.any(Function));
    });

    it('enableSearch sets data("onKeyUp") to true and calls luxPag.search with event value', function() {
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
        expect(LuxPagination.prototype.search).toHaveBeenCalledWith(mockEvent.srcElement.value, jasmine.any(String));
    });

    it('enableSearch doesn\'t call luxPag.search if query is less than three chars', function() {
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
        expect(LuxPagination.prototype.search).not.toHaveBeenCalled();
    });

    it('enableSearch returns if data().onKeyUp is true', function() {
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

    it('lazyLoad binds uiSelect to onscroll event and calls luxPag.loadMore if scroll offset reached', function() {
        var markup = '<div data-remote-options=\'{"url": "http://127.0.0.1:6050", "name": "groups_url"}\' data-remote-options-id="" name="groups[]" multiple="multiple"><input type="text"></input><ul class="ui-select-choices"><li class="ui-select-choices-group"></li></ul></div>';
        var elem = getCompiledElem(markup);
        var uiSelect = elem[0].querySelector('.ui-select-choices');
        uiSelect = angular.element(uiSelect);

        scope.$emit('moreData');
        uiSelect.triggerHandler('scroll');

        expect(LuxPagination.prototype.loadMore).toHaveBeenCalled();
    });
});
