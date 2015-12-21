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
                var triggered = false;

                if (!uiSelect) return;

                var uiSelectChild = uiSelect.querySelector('.ui-select-choices-group');
                uiSelect = angular.element(uiSelect);

                uiSelect.bind('scroll', function() {
                    // 40 = arbitrary number to make offset slightly smaller,
                    // this means the next api call will be just before the scroll
                    // bar reaches the bottom of the list
                    var offset = uiSelectChild.clientHeight - this.clientHeight - 40;

                    if (this.scrollTop >  offset && triggered === false) {
                        triggered = true;
                        luxPag.loadMore();
                    }
                });

            }

            function buildSelect(data) {
                // buildSelect
                if (data.error) return;

                angular.forEach(data.data.result, function (val) {
                    var name;
                    if (nameFromFormat) {
                        name = formatString(nameOpts.source, val);
                    } else {
                        name = val[nameOpts.source];
                    }
                    options.push({
                        id: val[id],
                        name: name
                    });
                });

            }

            var id = attrs.remoteOptionsId || 'id',
                nameOpts = attrs.remoteOptionsValue ? JSON.parse(attrs.remoteOptionsValue) : {
                        type: 'field',
                        source: 'id'
                    },
                nameFromFormat = nameOpts.type === 'formatString',
                initialValue = {},
                params = JSON.parse(attrs.remoteOptionsParams || '{}'),
                options = [];

            scope[target.name] = options;

            initialValue.id = '';
            initialValue.name = 'Loading...';

            options.push(initialValue);

            // Set empty value if field was not filled
            if (scope[scope.formModelName][attrs.name] === undefined)
                scope[scope.formModelName][attrs.name] = '';

            if (attrs.multiple) {
                options.splice(0, 1);
            } else {
                options[0].name = 'Please select...';
            }

            // Use LuxPagination's getData method to call the api
            // with relevant parameters and pass in buildSelect as callback
            luxPag.getData(params, buildSelect);
            // Listen for LuxPagination to emit 'moreData' then run lazyLoad
            scope.$on('moreData', lazyLoad);

        }

        function link(scope, element, attrs) {

            if (attrs.remoteOptions) {
                var target = JSON.parse(attrs.remoteOptions);
                var luxPag = new LuxPagination(scope, target);

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
