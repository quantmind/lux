define(['angular',
        'lux/forms/main',
        'angular-ui-select'], function (angular, lux) {
    'use strict';

    angular.module('lux.form.ui.select', ['lux.form', 'ui.select'])
        //
        .run(['$document', function ($document) {

            lux.forms.overrides.push(function (form) {

                var selectWidget = form.selectWidget;

                form.selectWidget = function (scope, element) {
                    // by default use selectUI unless switched of with ui=false attribute
                    if (scope.field.ui === false)
                        return selectWidget(scope, element);
                    else
                        return selectUiWidget(scope, element);
                };
            });

            //
            // UI-Select widget
            function selectUiWidget(scope, element) {
                var field = scope.field;
                //
                field.groupBy = function (item) {
                    return item.group;
                };

                field.element = 'ui-select';

                var select = angular.element(element[0].childNodes[1]),
                    model = select.attr('ng-model'),
                    selectUI =  angular.element($document[0].createElement(field.element))
                        .attr('id', field.id)
                        .attr('name', field.name)
                        .attr('ng-model', model),
                    match = angular.element($document[0].createElement('ui-select-match'))
                        .attr('placeholder', 'Select or search ' + field.label.toLowerCase()),
                    choices_inner = angular.element($document[0].createElement('span')),
                    //choices_inner_small = angular.element($document[0].createElement('small')),
                    choices = angular.element($document[0].createElement('ui-select-choices'))
                        .attr('ui-disable-choice', 'item.id === "placeholder"')
                        .append(choices_inner);

                var repeatItems = 'opt.repr || opt.value as opt in fields.' + field.name + '.options | filter: $select.search';

                choices
                    .attr('group-by', 'field.groupBy')
                    .attr('repeat', repeatItems);
                choices_inner.attr('ng-bind-html', 'opt.repr || opt.value');

                // choices_inner_small.attr('ng-bind-html', 'opt.repr || opt.value');
                // choices.append(choices_inner_small);

                if (field.theme)
                    selectUI.attr('theme', field.theme);

                if (field.hasOwnProperty('search'))
                    selectUI.attr('search-enabled', field.search);

                if (field.multiple) {
                    selectUI.attr('multiple', true);
                    match.html('{{$item.value || $item.repr || $item.name || $item.id}}');
                } else
                    match.html('{{$select.selected.repr || $select.selected.value}}');

                selectUI.append(match);
                selectUI.append(choices);
                element[0].replaceChild(selectUI[0], select[0]);
            }

        }]);

});
