
export default function (ngModule) {
    ngModule.config(addWrappers);
    
    // @ngInject
    function addWrappers(luxFormConfigProvider) {
        var p = luxFormConfigProvider;

        p.setWrapper({
            name: 'bootstrapLabel',
            template: labelTpl
        });

        p.setWrapper({
            name: 'bootstrapStatus',
            template: statusTpl
        });

    }
}


const labelTpl = function (inner) {
    return `<label for="{{field.id}}" class="control-label {{field.labelSrOnly ? 'sr-only' : ''}}" ng-if="field.label">
    {{field.label}}
    {{field.required ? '*' : ''}}
  </label>
  ${inner}`;
}


const statusTpl = function (inner) {
    return `<div class="form-group" ng-class="{'has-error': field.error, 'has-success': field.success}">
${inner}
<p ng-if="field.error" class="text-danger error-block">{{ field.error }}</p>
</div>`;
}
