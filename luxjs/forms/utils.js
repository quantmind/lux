/**
 * Created by Reupen on 02/06/2015.
 */

angular.module('lux.form.utils', ['lux.services', 'lux.pagination'])

    .directive('remoteOptions', ['$lux', 'LuxPagination', '$timeout', function ($lux, LuxPagination, $timeout) {

        function remoteOptions(luxPag, target, scope, attrs, element) {

            function lazyLoad() {
                var uiSelect = element[0].querySelector('.ui-select-choices');
                var triggered = false;

                if (!uiSelect) return;

                var uiSelectChild = uiSelect.querySelector('.ui-select-choices-group');
                uiSelect = angular.element(uiSelect);

                uiSelect.bind('scroll', function() {
                    var offset = uiSelectChild.clientHeight - this.clientHeight - 40;

                    if (this.scrollTop >  offset && triggered === false) {
                        triggered = true;
                        luxPag.loadMore();
                    }
                });

            }

            function buildSelect(data) {

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

            luxPag.getData(params, buildSelect);

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
