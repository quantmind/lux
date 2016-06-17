import {compileUiSelect} from './remote';
import {defaultPlaceholder, selectOptions} from './utils';
import {FormElement, Form, Field, Formset} from './objects';

// Set default types
export default function (ngModule) {
    ngModule.config(addTypes);

    // @ngInject
    function addTypes(luxFormConfigProvider) {
        var p = luxFormConfigProvider;

        p.setType({
            name: 'form',
            template: formTemplate,
            class: Form
        });

        // Inputs
        p.setType({
            name: 'input',
            template: inputTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
            class: Field,
            defaultOptions: function (field) {
                return {
                    title: field.name,
                    placeholder: defaultPlaceholder(field),
                    disabled: false,
                    value: ''
                };
            }
        });

        // Checkbox
        p.setType({
            name: 'checkbox',
            template: checkboxTpl,
            class: Field
        });

        // Radio
        p.setType({
            name: 'radio',
            template: radioTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
            class: Field
        });

        // Select
        p.setType({
            name: 'select',
            template: selectTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
            class: Field,
            defaultOptions: function (field) {
                return {
                    placeholder: defaultPlaceholder(field),
                    options: selectOptions(field)
                };
            }
        });

        // UI-Select
        p.setType({
            name: 'ui-select',
            template: uiSelectTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
            class: Field,
            defaultOptions: function (field) {
                return {
                    placeholder: defaultPlaceholder(field),
                    options: selectOptions(field)
                };
            },
            compile: compileUiSelect
        });

        // Textarea
        p.setType({
            name: 'textarea',
            template: textareaTpl,
            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
            class: Field,
            defaultOptions: function (field) {
                return {
                    placeholder: defaultPlaceholder(field),
                    rows: 10
                };
            }
        });

        // Button / Submit
        p.setType({
            name: 'button',
            template: buttonTpl,
            class: Field,
            defaultOptions: function (field) {
                return {
                    label: field.name,
                    type: 'submit',
                    value: field.name
                };
            }
        });

        // Anchor
        p.setType({
            name: 'a',
            template: anchorTpl,
            class: FormElement,
            defaultOptions: function (field) {
                return {
                    title: field.href || ''
                };
            }
        });

        // Fieldset
        p.setType({
            name: 'fieldset',
            class: FormElement,
            template: fieldsetTpl
        });

        // Div
        p.setType({
            name: 'row',
            class: FormElement,
            template: rowTpl
        });

        p.setType({
            name: 'col',
            class: FormElement,
            template: colTpl,
            defaultOptions: {
                size: 12
            }
        });

        // formset
        p.setType({
            name: 'formset',
            class: Formset,
            template: formsetTemplate
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
${field.directives}
ng-model="field.value"
ng-required="${field.required}"
ng-readonly="${field.readonly}"
ng-disabled="${field.disabled}"
ng-minlength="${field.minlength}"
ng-maxlength="${field.maxlength}"
>`;
}

function selectTpl (field) {
    return `<select class="form-control"
id="${field.id}"
name="${field.name}"
${field.directives}
ng-model="field.value"
ng-options="option.label for option in field.options track by option.value"
ng-required="${field.required}"
ng-readonly="${field.readonly}"
ng-disabled="${field.disabled}"
>
</select>`;
}

function textareaTpl (field) {
    return `<textarea class="form-control"
id="${field.id}"
name="${field.name}"
placeholder="${field.placeholder}"
rows="${field.rows}"
${field.directives}
ng-model="field.value"
ng-required="${field.required}"
ng-readonly="${field.readonly}"
ng-disabled="${field.disabled}">
"${field.value}"
</textarea>`;
}


function checkboxTpl (field) {
    return `<div class="checkbox">
<label>
<input type="checkbox"
ng-model="field.value">
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
             ng-model="field.value">
      {{option[to.labelProp || 'name']}}
    </label>
  </div>
</div>
`;


function fieldsetTpl (field) {
    var legend = field.legend || ``;
    if (legend) legend = `<legend>${legend}</legend>`;
    return `<fieldset>${legend}</fieldset>`;
}

const rowTpl = `<div class="row"></div>`;


function colTpl(field) {
    return `<div class="col-sm-${field.size}"></div>`;
}


function buttonTpl(field) {
    return `<button name="${field.name}"
class="btn btn-default"
ng-disabled="${field.disabled}"
type="${field.type}"
ng-click="field.$click($event)"
>${field.label}</button>`;
}


function anchorTpl (field) {
    var icon = '',
        theme = field.theme || 'default';
    if (field.icon) icon = `<i aria-hidden="true" class="${field.icon}"></i>`;

    return `<a class="btn btn-${theme}"
href="#"
ng-click="field.$click($event)"
title="${field.title}"
ng-hide="${field.hide}"
>${icon}</a>`;
}


function uiSelectTpl(field) {
    return `<div class="input-group">
<ui-select
id="${field.id}"
name="${field.name}"
${field.directives}
theme="bootstrap"
ng-model="field.value"
ng-required="${field.required}"
ng-readonly="${field.readonly}"
ng-disabled="${field.disabled}"
allow-clear>
<ui-select-match placeholder="${field.placeholder}">{{$select.selected.label}}</ui-select-match>
<ui-select-choices repeat="item.value as item in field.options | filter: $select.search">
  <div ng-bind-html="item.label | highlight: $select.search"></div>
  <small ng-if="item.description" ng-bind-html="item.description | highlight: $select.search"></small>
</ui-select-choices>
</ui-select>
<span class="input-group-btn">
  <button type="button" ng-click="field.value = '" class="btn btn-default">
    <span class="glyphicon glyphicon-trash"></span>
  </button>
</span>
</div>`;
}


function formTemplate (form) {
    return `<${form.tag} name="${form.name}" role="form" class="${form.classes}" novalidate>
</${form.tag}>`;
}


function formsetTemplate () {
    return `<lux-formset ng-repeat="model in formset.value"
field="field"
model="model"
formset="formset">
</lux-formset>`;
}
