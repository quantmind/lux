import rest from './rest';


// @ngInject
export default function (luxGridProvider) {
    
    luxGridProvider.registerDataProvider('rest', rest);
}
