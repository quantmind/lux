define(['angular',
        'lux/main',
        'lux/services/pagination'], function (angular, lux) {
    'use strict';

    angular.module('lux.form.utils', ['lux.pagination'])

        .constant('lazyLoadOffset', 40) // API will be called this number of pixels
                                        // before bottom of UIselect list

        .directive('remoteOptions', ['$lux', 'luxPaginationFactory', 'lazyLoadOffset',
            function ($lux, LuxPagination, lazyLoadOffset) {

                return {
                    link: link
                };

                function remoteOptions(luxPag, target, scope, attrs, element) {

                    function lazyLoad(e) {
                        // lazyLoad requests the next page of data from the API
                        // when nearing the bottom of a <select> list
                        var uiSelect = element[0].querySelector('.ui-select-choices');

                        e.stopPropagation();
                        if (!uiSelect) return;

                        var uiSelectChild = uiSelect.querySelector('.ui-select-choices-group');
                        uiSelect = angular.element(uiSelect);

                        uiSelect.on('scroll', function () {
                            var offset = uiSelectChild.clientHeight - this.clientHeight - lazyLoadOffset;

                            if (this.scrollTop > offset) {
                                uiSelect.off();
                                luxPag.loadMore();
                            }
                        });

                    }

                    function enableSearch() {
                        if (searchInput.data().onKeyUp) return;

                        searchInput.data('onKeyUp', true);
                        searchInput.on('keyup', function (e) {
                            var query = e.srcElement.value;
                            var searchField = attrs.remoteOptionsId === 'id' ? nameOpts.source : attrs.remoteOptionsId;

                            cleanSearchResults();

                            // Only call API with search if query is > 3 chars
                            if (query.length > 3) {
                                luxPag.search(query, searchField);
                            }
                        });
                    }

                    function loopAndPush(data) {
                        angular.forEach(data.data.result, function (val) {
                            var name;
                            if (nameFromFormat) {
                                name = lux.formatString(nameOpts.source, val);
                            } else {
                                name = val[nameOpts.source];
                            }

                            options.push({
                                id: val[id],
                                name: name,
                                searched: data.searched ? true : false
                            });
                        });

                        cleanDuplicates();
                    }

                    function cleanSearchResults() {
                        // options objects containing data.searched will be removed
                        // after relevant search.
                        for (var i = 0; i < options.length; i++) {
                            if (options[i].searched) options.splice(i, 1);
                        }
                    }

                    function cleanDuplicates() {
                        // $timeout waits for rootScope.$digest to finish,
                        // then removes duplicates from options list on the next tick.
                        $lux.timeout(function () {
                            return scope.$select.selected;
                        }).then(function (selected) {
                            for (var a = 0; a < options.length; a++) {
                                for (var b = 0; b < selected.length; b++) {
                                    if (options[a].id === selected[b].id) options.splice(a, 1);
                                }
                            }
                        });
                    }

                    function buildSelect(data) {
                        // buildSelect uses data from the API to populate
                        // the options variable, which builds our <select> list
                        if (data.data && data.data.error) {
                            options.splice(0, 1, {
                                id: 'placeholder',
                                name: 'Unable to load data...'
                            });
                            throw new Error(data.data.message);
                        } else {
                            loopAndPush(data);
                        }
                    }

                    var id = attrs.remoteOptionsId || 'id';
                    var nameOpts = attrs.remoteOptionsValue ? angular.fromJson(attrs.remoteOptionsValue) : {
                        type: 'field',
                        source: 'id'
                    };
                    var nameFromFormat = nameOpts.type === 'formatString';
                    var initialValue = {};
                    var params = angular.fromJson(attrs.remoteOptionsParams || '{}');
                    var options = [];
                    var searchInput = angular.element(element[0].querySelector('input[type=text]'));

                    scope[target.name] = options;

                    initialValue.id = '';
                    initialValue.name = 'Loading...';

                    options.push(initialValue);

                    // Set empty value if field was not filled
                    if (angular.isUndefined(scope[scope.formModelName][attrs.name])) {
                        scope[scope.formModelName][attrs.name] = '';
                    }

                    if (attrs.multiple) {
                        // Increasing default API call limit as UISelect multiple
                        // displays all preselected options
                        params.limit = 200;
                        params.sortby = nameOpts.source ? nameOpts.source + ':asc' : 'id:asc';
                        options.splice(0, 1);
                    } else {
                        params.sortby = params.sortby ? params.sortby + ':asc' : 'id:asc';
                        // Options with id 'placeholder' are disabled in
                        // forms.js so users can't select them
                        options[0] = {
                            name: 'Please select...',
                            id: 'placeholder'
                        };
                    }

                    // Use LuxPagination's getData method to call the api
                    // with relevant parameters and pass in buildSelect as callback
                    luxPag.getData(params, buildSelect);
                    // Listen for LuxPagination to emit 'moreData' then run
                    // lazyLoad and enableSearch
                    scope.$on('moreData', function (e) {
                        lazyLoad(e);
                        enableSearch();
                    });
                }

                function link(scope, element, attrs) {

                    if (attrs.remoteOptions) {
                        var target = angular.fromJson(attrs.remoteOptions);
                        var luxPag = new LuxPagination(scope, target, attrs.multiple ? true : false);

                        if (luxPag && target.name)
                            return remoteOptions(luxPag, target, scope, attrs, element);
                    }

                    // TODO: message
                }
            }
        ])

        .directive('selectOnClick', ['$window', function ($window) {
            return {
                restrict: 'A',
                link: function (scope, element) {
                    element.on('click', function () {
                        if (!$window.getSelection().toString()) {
                            // Required for mobile Safari
                            this.setSelectionRange(0, this.value.length);
                        }
                    });
                }
            };
        }])
        //
        .directive('checkRepeat', ['$log', function (log) {
            return {
                require: 'ngModel',

                restrict: 'A',

                link: function(scope, element, attrs, ctrl) {
                    var other = element.inheritedData('$formController')[attrs.checkRepeat];
                    if (other) {
                        ctrl.$parsers.push(function(value) {
                            if(value === other.$viewValue) {
                                ctrl.$setValidity('repeat', true);
                                return value;
                            }
                            ctrl.$setValidity('repeat', false);
                        });

                        other.$parsers.push(function(value) {
                            ctrl.$setValidity('repeat', value === ctrl.$viewValue);
                            return value;
                        });
                    } else {
                        log.error('Check repeat directive could not find ' + attrs.checkRepeat);
                    }
                }
            };
        }]);

});
