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
        last = last = {
            label: 'Home',
            href: '/'
        };

    steps.push(last);
    
    path.split('/').forEach(function (name) {
        if (name) {
            last = {
                label: name.split(/[-_]+/).map(capitalize).join(' '),
                href: urlJoin(last.href, name)
            };
            steps.push(last);
        }
    });
    steps[steps.length-1].last = true;

    return steps;
}


const crumbsTemplate = `<ol class="breadcrumb">
    <li ng-repeat="step in steps" ng-class="{active: step.last}">
        <a ng-if="!step.last" href="{{step.href}}">{{step.label}}</a>
        <span ng-if="step.last">{{step.label}}</span>
    </li>
</ol>`;
