define(['angular',
        'lux/forms/main',
        'angular-ui-select'], function (angular, lux) {
    'use strict';

    angular.module('lux.form.ui.select', ['lux.form', 'ui.select'])

        .run(['$document', function ($document) {
            lux.forms.overrides.push(function (form) {

                var selectWidget = form.selectWidget,
                    elements = form.elements;

                form.selectWidget = function (scope, element, field, groupList, options) {
                    if (elements.select.hasOwnProperty('widget') && elements.select.widget.name === 'selectUI')
                    // UI-Select widget
                        return selectUiWidget(scope, element, field, groupList, options);
                    else
                        return selectWidget(scope, element, field, groupList, options);
                };
                //
                // UI-Select widget
                function selectUiWidget(scope, element, field, groupList, options) {
                    //
                    scope.groupBy = function (item) {
                        return item.group;
                    };
                    // Search specified global
                    scope.enableSearch = elements.select.widget.enableSearch;

                    // Search specified for field
                    if (field.hasOwnProperty('search'))
                        scope.enableSearch = field.search;

                    var selectUI = angular.element($document[0].createElement('ui-select'))
                        .attr('id', field.id)
                        .attr('name', field.name)
                        .attr('ng-model', scope.formModelName + '["' + field.name + '"]')
                        .attr('theme', elements.select.widget.theme)
                        .attr('search-enabled', 'enableSearch')
                        .attr('ng-change', 'fireFieldChange("' + field.name + '")'),
                        match = angular.element($document[0].createElement('ui-select-match'))
                            .attr('placeholder', 'Select or search ' + field.label.toLowerCase()),
                        choices_inner = angular.element($document[0].createElement('div')),
                        choices_inner_small = angular.element($document[0].createElement('small')),
                        choices = angular.element($document[0].createElement('ui-select-choices'))
                        // Ensure any inserted placeholders are disabled
                        // i.e. 'Please Select...'
                            .attr('ui-disable-choice', 'item.id === "placeholder"')
                            .append(choices_inner);

                    if (field.multiple)
                        selectUI.attr('multiple', true);

                    if (field.hasOwnProperty('data-remote-options')) {
                        // Remote options
                        selectUI.attr('data-remote-options', field['data-remote-options'])
                            .attr('data-remote-options-id', field['data-remote-options-id'])
                            .attr('data-remote-options-value', field['data-remote-options-value'])
                            .attr('data-remote-options-params', field['data-remote-options-params']);

                        if (field.multiple)
                            match.html('{{$item.repr || $item.name || $item.id}}');
                        else
                            match.html('{{$select.selected.name || $select.selected.id}}');

                        choices.attr('repeat', field['data-ng-options-ui-select'] + ' | filter: $select.search');
                        choices_inner.html('{{item.name || item.id}}');
                    } else {
                        // Local options
                        var optsId = field.name + '_opts',
                            repeatItems = 'opt.value as opt in ' + optsId + ' | filter: $select.search';

                        if (field.multiple)
                            match.html('{{$item.value}}');
                        else
                            match.html('{{$select.selected.value}}');

                        if (groupList.length) {
                            // Groups require raw options
                            scope[optsId] = field.options;
                            choices.attr('group-by', 'groupBy')
                                .attr('repeat', repeatItems);
                            choices_inner.attr('ng-bind-html', 'opt.repr || opt.value');
                        } else {
                            scope[optsId] = options;
                            choices.attr('repeat', repeatItems);

                            if (options.length > 0) {
                                var attrsNumber = Object.keys(options[0]).length;
                                choices_inner.attr('ng-bind-html', 'opt.repr || opt.value');

                                if (attrsNumber > 1) {
                                    choices_inner_small.attr('ng-bind-html', 'opt.value');
                                    choices.append(choices_inner_small);
                                }
                            }
                        }
                    }

                    selectUI.append(match);
                    selectUI.append(choices);
                    element[0].replaceChild(selectUI[0], element[0].childNodes[1]);
                }
            });
        }]);

});
