import capitalize from '../core/capitalise';
import {urlJoin} from '../core/urls';


// @ngInject
export default function ($location) {
    return {
        restrict: 'AE',
        replace: true,
        template: crumbsTemplate,
        controller: CrumbsCtrl
    };

    // @ngInject
    function CrumbsCtrl ($scope) {
        $scope.steps = crumbs($location);
    }
}


function crumbs (loc) {
    var steps = [],
        path = loc.path(),
        last;

    path.split('/').forEach(function (name) {
        if (!name) {
            last = {
                label: 'Home',
                href: '/'
            };
        } else {
            last = {
                label: name.split(/[-_]+/).map(capitalize).join(' '),
                href: urlJoin(last.href, name)
            };
        }
        steps.push(last);
    });

    return steps;
}


const crumbsTemplate = `<ol class="breadcrumb">
    <li ng-repeat="step in steps" ng-class="{active: step.last}">
        <a ng-if="!step.last" href="{{step.href}}">{{step.label}}</a>
        <span ng-if="step.last">{{step.label}}</span>
    </li>
</ol>`;
