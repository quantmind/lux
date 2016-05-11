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
}
