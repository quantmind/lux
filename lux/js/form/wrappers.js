
export default function (ngModule) {
    ngModule.config(['luxFormConfigProvider', addWrappers]);

    function addWrappers(luxFormConfigProvider) {
        var p = luxFormConfigProvider;

        p.setWrapper({
            name: 'bootstrapLabel',
            template: labelTpl
        });

        p.setWrapper({
            name: 'bootstrapHasError',
            template: errorTpl
        });

    }
}


const labelTpl = function (inner) {
    return `<div>
  <label for="{{id}}" class="control-label {{to.labelSrOnly ? 'sr-only' : ''}}" ng-if="to.label">
    {{to.label}}
    {{to.required ? '*' : ''}}
  </label>
  ${inner}
</div>`;
}


const errorTpl = function (inner) {
    return `<div class="form-group" ng-class="{'has-error': showError}">
  ${inner}
</div>`;
}
