
export default function (ngModule) {
    ngModule.config(['luxFormConfigProvider', addTypes]);

    function addTypes(luxFormConfigProvider) {
        var p = luxFormConfigProvider;

        // Inputs
        p.setType({
            name: 'input',
            template: `<input class="form-control" ng-model="model[options.key]">`,
            wrapper: ['bootstrapLabel', 'bootstrapHasError']
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
            template: `<select class="form-control" ng-model="model[options.key]"></select>`,
            wrapper: ['bootstrapLabel', 'bootstrapHasError']
        });

        // Textarea
        p.setType({
            name: 'textarea',
            template: `<textarea class="form-control" ng-model="model[options.key]"></textarea>`,
            wrapper: ['bootstrapLabel', 'bootstrapHasError'],
            defaultOptions: {
                ngModelAttrs: {
                    rows: {attribute: 'rows'},
                    cols: {attribute: 'cols'}
                }
            }
        });
    }
}

const checkboxTpl = `
<div class="checkbox">
<label>
        <input type="checkbox"
           class="formly-field-checkbox"
               ng-model="model[options.key]">
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
             ng-model="model[options.key]">
      {{option[to.labelProp || 'name']}}
    </label>
  </div>
</div>
`
