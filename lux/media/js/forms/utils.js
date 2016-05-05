define(['angular',
        'lux/main',
        'lux/pagination/main'], function (angular, lux) {
    'use strict';

    angular.module('lux.form.utils', ['lux.pagination'])

        .constant('lazyLoadOffset', 40) // API will be called this number of pixels
                                        // before bottom of UIselect list

        .factory('remoteSelect', ['$timeout', 'lazyLoadOffset', function ($timeout, lazyLoadOffset) {

            return remoteSelect;

            function remoteSelect(scope) {
                var api = scope.api;
                if (!api) return;

                var model = scope[scope.formModelName],
                    field = scope.field,
                    value = model[field.name];

                scope.options.push({id: '', name: 'Loading...'});


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
                    $timeout(function () {
                        return scope.$select.selected;
                    }).then(function (selected) {
                        for (var a = 0; a < options.length; a++) {
                            for (var b = 0; b < selected.length; b++) {
                                if (options[a].id === selected[b].id) options.splice(a, 1);
                            }
                        }
                    });
                }

                function buildSelect(response) {
                    // buildSelect uses data from the API to populate
                    // the options variable, which builds our <select> list
                    var data = response.data;

                    if (data && data.error) {
                        scope.options.splice(0, 1, {
                            id: 'placeholder',
                            name: 'Unable to load data...'
                        });
                    } else {
                        angular.forEach(data.result, function (val) {
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
                }

                // Use luxPagination's getData method to call the api
                // with relevant parameters and pass in buildSelect as callback
                api.get().then(buildSelect);
                // Listen for luxPagination to emit 'moreData' then run
                // lazyLoad and enableSearch
                scope.$on('moreData', function (e) {
                    lazyLoad(e);
                    enableSearch();
                });
            }

        }])

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
