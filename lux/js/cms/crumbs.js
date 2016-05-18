import capitalize from '../core/capitalise';
import {urlJoin} from '../core/urls';


// @ngInject
export default function ($window) {
    return {
        restrict: 'AE',
        replace: true,
        template: crumbsTemplate,
        controller: CrumbsCtrl
    };

    // @ngInject
    function CrumbsCtrl ($scope) {
        $scope.steps = crumbs($window.location);
    }
}


function crumbs (loc) {
    var path = loc.pathname,
        steps = [],
        base = loc.url,
        last = {
            href: loc.origin
        };
    if (last.href.length >= base.length)
        steps.push(last);

    path.split('/').forEach(function (name) {
        if (name) {
            last = {
                label: name.split(/[-_]+/).map(capitalize).join(' '),
                href: urlJoin(last.href, name)
            };
            if (last.href.length >= base.length)
                steps.push(last);
        }
    });
    if (steps.length) {
        last = steps[steps.length - 1];
        if (path.substring(path.length - 1) !== '/' && last.href.substring(last.href.length - 1) === '/')
            last.href = last.href.substring(0, last.href.length - 1);
        last.last = true;
        steps[0].label = 'Home';
    }
    return steps;
}


const crumbsTemplate = `<ol class="breadcrumb">
    <li ng-repeat="step in steps" ng-class="{active: step.last}">
        <a ng-if="!step.last" href="{{step.href}}">{{step.label}}</a>
        <span ng-if="step.last">{{step.label}}</span>
    </li>
</ol>`;
