import rest from './rest';
import * as utils from './utils';


// @ngInject
export default function (luxGridProvider) {

    luxGridProvider.registerDataProvider('rest', rest);

    luxGridProvider
        .columnProcessor('date', utils.dateColumn)
        .columnProcessor('datetime', utils.dateColumn)
        .columnProcessor('boolean', utils.booleanColumn)
        .columnProcessor('string', utils.stringColumn)
        .columnProcessor('url', utils.urlColumn)
        .columnProcessor('object', utils.objectColumn)
        .onInit(utils.paginationEvents);
    
    luxGridProvider.defaults.gridMenu = {
        'create': {
            title: 'Add',
            icon: 'fa fa-plus',
            permissionType: 'create'
        },
        'delete': {
            title: 'Delete',
            icon: 'fa fa-trash',
            permissionType: 'delete',
            template: deleteTpl
        },
        'columnsVisibility': {
            title: 'Columns visibility',
            icon: 'fa fa-eye'
        }
    };
}


const deleteTpl = `<div class="modal-header">
    <button type="button" class="close" aria-label="Close" ng-click="$dismiss()"><span aria-hidden="true">&times;</span></button>
    <h4 class="modal-title"><i class="fa fa-trash"></i> Delete {{stateName}}</h4>
</div>
<div class="modal-body">
    <p class="modal-info">{{infoMessage}}</p>
    <ul class="modal-items">
        <li ng-repeat="item in selected">{{item[repr_field]}}</li>
    </ul>
    <p class="text-danger cannot-undo">{{dangerMessage}}</p>
</div>
<div class="modal-footer">
    <button type="button" class="btn btn-primary" ng-click="$close()">Yes</button>
    <button type="button" class="btn btn-default" ng-click="$dismiss()">No</button>
</div>`;
