/**
 * Created by Reupen on 02/06/2015.
 * Edited by Tom on 18/12/2015.
 */

angular.module('lux.form.utils', ['lux.services', 'lux.pagination'])

    .directive('remoteOptions', ['$lux', 'LuxPagination', function ($lux, LuxPagination) {

        function remoteOptions(luxPag, target, scope, attrs, element) {

            function lazyLoad(e) {
                // lazyLoad requests the next page of data from the API
                // when nearing the bottom of a <select> list
                var uiSelect = element[0].querySelector('.ui-select-choices');

                e.stopPropagation();
                if (!uiSelect) return;

                var uiSelectChild = uiSelect.querySelector('.ui-select-choices-group');
                uiSelect = angular.element(uiSelect);

                uiSelect.bind('scroll', function() {
                    // 40 = arbitrary number to make offset slightly smaller,
                    // this means the next api call will be just before the scroll
                    // bar reaches the bottom of the list
                    var offset = uiSelectChild.clientHeight - this.clientHeight - 40;

                    if (this.scrollTop > offset) {
                        uiSelect.unbind();
                        luxPag.loadMore();
                    }
                });

            }

            function enableSearch() {
                searchInput.bind('keyup', function(e) {
                    var query = e.srcElement.value;
                    var searchField = attrs.remoteOptionsId === 'id' ? nameOpts.source : attrs.remoteOptionsId;

                    // Only call API with search if query is > 3 chars
                    if (query.length > 3) {
                        luxPag.search(query, searchField);
                    }
                });
            }

            function buildSelect(data) {
                // buildSelect uses data from the API to populate
                // the options variable, which builds our <select> list
                if (data.error) return;

                angular.forEach(data.data.result, function (val) {
                    var name;
                    if (nameFromFormat) {
                        name = formatString(nameOpts.source, val);
                    } else {
                        name = val[nameOpts.source];
                    }

                    // If the value already exists in the select, don't
                    // add it again.
                    for (var i=0; i<options.length; i++) {
                        if (options[i].id === val[id]) return;
                    }

                    options.push({
                        id: val[id],
                        name: name
                    });

                });
                // Sort list alphabetically by name.
                options.sort(function(a,b) {
                    // Ensure 'please select' remains at the top
                    if (a.name === 'Please select...') return -1;
                    if (a.name > b.name) {
                        return 1;
                    }
                    if (a.name < b.name) {
                        return -1;
                    }
                    return 0;
                });
            }

            var id = attrs.remoteOptionsId || 'id';
            var nameOpts = attrs.remoteOptionsValue ? JSON.parse(attrs.remoteOptionsValue) : {
                    type: 'field',
                    source: 'id'
                };
            var nameFromFormat = nameOpts.type === 'formatString';
            var initialValue = {};
            var params = JSON.parse(attrs.remoteOptionsParams || '{}');
            var options = [];
            var searchInput = angular.element(element[0].querySelector('input[type=text]'));

            scope[target.name] = options;

            initialValue.id = '';
            initialValue.name = 'Loading...';

            options.push(initialValue);

            // Set empty value if field was not filled
            if (scope[scope.formModelName][attrs.name] === undefined) {
                scope[scope.formModelName][attrs.name] = '';
            }

            if (attrs.multiple) {
                options.splice(0, 1);
                // Increasing default API call limit as UISelect multiple
                // displays all preselected options
                params.limit = 250;
            } else {
                // This option should be disabled
                options[0] = {
                    name: 'Please select...',
                    id: 'placeholder'
                };
            }

            // Use LuxPagination's getData method to call the api
            // with relevant parameters and pass in buildSelect as callback
            luxPag.getData(params, buildSelect);
            // Listen for LuxPagination to emit 'moreData' then run lazyLoad
            // lazyLoad and enableSearch
            scope.$on('moreData', function() {
                lazyLoad();
                enableSearch();
            });
        }

        function link(scope, element, attrs) {

            if (attrs.remoteOptions) {
                var target = JSON.parse(attrs.remoteOptions);
                var luxPag = new LuxPagination(scope, target, attrs.multiple ? true : false);

                if (luxPag && target.name)
                    return remoteOptions(luxPag, target, scope, attrs, element);
            }

            // TODO: message
        }

        return {
            link: link
        };
    }])

    .directive('selectOnClick', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                element.on('click', function () {
                    if (!window.getSelection().toString()) {
                        // Required for mobile Safari
                        this.setSelectionRange(0, this.value.length);
                    }
                });
            }
        };
    });
