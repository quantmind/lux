
export default function (ngModule) {
    ngModule.config(['luxFormConfigProvider', addTypes]);

    function addTypes(luxFormConfigProvider) {
        var p = luxFormConfigProvider;

        // Inputs
        p.setType({
            name: 'input',
            template: inputTpl,
            wrapper: ['bootstrapLabel', 'bootstrapHasError'],
            defaultOptions: function (field) {
                return {
                    title: field.name,
                    value: ''
                }
            }
        });

        // Checkbox
        p.setType({
            name: 'checkbox',
            template: checkboxTpl,
            wrapper: ['bootstrapHasError']
        });

        // Radio
        p.setType({
            name: 'radio',
            template: radioTpl,
            wrapper: ['bootstrapLabel', 'bootstrapHasError']
        });

        // Select
        p.setType({
            name: 'select',
            template: `<select class="form-control" ng-model="model[field.name]"></select>`,
            wrapper: ['bootstrapLabel', 'bootstrapHasError']
        });

        // Textarea
        p.setType({
            name: 'textarea',
            template: `<textarea class="form-control" ng-model="model[field.name]"></textarea>`,
            wrapper: ['bootstrapLabel', 'bootstrapHasError'],
            defaultOptions: {
                ngModelAttrs: {
                    rows: {attribute: 'rows'},
                    cols: {attribute: 'cols'}
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
ng-model="model['${field.name}']"
ng-required="field.required"
ng-readonly="field.readonly"
ng-disabled="field.disabled"
ng-minlength="field.minlength"
ng-maxlength="field.minlength"
>`
}

const checkboxTpl = `
<div class="checkbox">
<label>
        <input type="checkbox"
           class="formly-field-checkbox"
               ng-model="model[field.name]">
        {{to.label}}
        {{to.required ? '*' : ''}}
    </label>
</div>
`


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
