import {selectOptions, compileUiSelect} from './remote';


// Set default types
export default function (ngModule) {
    ngModule.config(addTypes);
    
    // @ngInject
    function addTypes(luxFormConfigProvider) {
        var p = luxFormConfigProvider;

        // Inputs
        p.setType({
            name: 'input',
            template: inputTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
            defaultOptions: function (field) {
                return {
                    title: field.name,
                    placeholder: field.label || field.name,
                    labelSrOnly: field.showLabels === false || field.type === 'hidden',
                    value: ''
                }
            }
        });

        // Checkbox
        p.setType({
            name: 'checkbox',
            template: checkboxTpl
        });

        // Radio
        p.setType({
            name: 'radio',
            template: radioTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus']
        });

        // Select
        p.setType({
            name: 'select',
            template: selectTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
            defaultOptions: function (field) {
                var options = field.options;
                delete field.options;
                return {
                    options: selectOptions(options)
                };
            }
        });

        // UI-Select
        p.setType({
            name: 'ui-select',
            template: uiSelectTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
            defaultOptions: function (field) {
                var options = field.options;
                delete field.options;
                return {
                    options: selectOptions(options)
                };
            },
            compile: compileUiSelect
        });

        // Textarea
        p.setType({
            name: 'textarea',
            template: textareaTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
            defaultOptions: function (field) {
                return {
                    placeholder: field.label || field.name,
                    ngModelAttrs: {
                        rows: {attribute: 'rows'},
                        cols: {attribute: 'cols'}
                    }
                };
            }
        });

        // Button / Submit
        p.setType({
            name: 'button',
            template: buttonTpl,
            defaultOptions: function (field) {
                return {
                    label: field.name,
                    type: 'submit',
                    value: field.name
                    //disabled: "form.$invalid"
                }
            }
        });

        // Fieldset
        p.setType({
            name: 'fieldset',
            template: fieldsetTpl,
            group: true
        });

        // Div
        p.setType({
            name: 'div',
            group: true
        });
    }
}

function inputTpl(field) {
    return `<input class="form-control" 
id="${field.id}"
name="${field.name}"
type="${field.type}"
value="${field.value}"
title="${field.title}"
placeholder="${field.placeholder}"
${field.directives}"
ng-model="model['${field.name}']"
ng-required="field.required"
ng-readonly="field.readonly"
ng-disabled="field.disabled"
ng-minlength="field.minlength"
ng-maxlength="field.minlength"
>`
}

function selectTpl (field) {
    return `<select class="form-control"
id="${field.id}"
name="${field.name}"
${field.directives}"
ng-model="model['${field.name}']"
ng-options="option.label for option in field.options track by option.value"
ng-required="field.required"
ng-readonly="field.readonly"
ng-disabled="field.disabled"
>
</select>`
}

function textareaTpl (field) {
    return `<textarea class="form-control"
id="${field.id}"
name="${field.name}"
placeholder="${field.placeholder}"
${field.directives}"
ng-model="model['${field.name}']"
ng-required="field.required"
ng-readonly="field.readonly"
ng-disabled="field.disabled">
"${field.value}"
</textarea>`;
}


function checkboxTpl (field) {
    return `<div class="checkbox">
<label>
<input type="checkbox"
ng-model="model['${field.name}']">
${field.label}
</label>
</div>`;
}


const radioTpl = `
<div class="radio-group">
  <div ng-repeat="(key, option) in to.options" ng-class="{ 'radio': !to.inline, 'radio-inline': to.inline }">
    <label>
      <input type="radio"
             id="{{id + '_'+ $index}}"
             tabindex="0"
             ng-value="option[to.valueProp || 'value']"
             ng-model="model[field.name]">
      {{option[to.labelProp || 'name']}}
    </label>
  </div>
</div>
`


function fieldsetTpl (field) {
    var legend = field.legend || ``;
    if (legend) legend = `<legend>${legend}</legend>`;
    return `<fieldset>${legend}</fieldset>`
}


function buttonTpl(field) {
    return `<button name="${field.name}"
class="btn btn-default"
ng-disabled="field.disabled"
type="${field.type}"
ng-click="field.$click($event)"
>${field.label}</button>`
}


function uiSelectTpl(field) {
    return `<ui-select class="form-control"
id="${field.id}"
name="${field.name}"
${field.directives}"
ng-model="model['${field.name}']"
ng-options="option.label for option in field.options track by option.value"
ng-required="field.required"
ng-readonly="field.readonly"
ng-disabled="field.disabled"
theme="bootstrap"
>
<ui-select-match placeholder="Select or search a person in the list...">{{$select.selected.name}}</ui-select-match>
<ui-select-choices repeat="item in field.options | filter: $select.search">
  <div ng-bind-html="item.label | highlight: $select.search"></div>
  <small ng-if="item-description" ng-bind-html="item.description | highlight: $select.search"></small>
</ui-select-choices>
</ui-select>`
}
