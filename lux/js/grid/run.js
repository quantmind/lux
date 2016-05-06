import rest from './rest';


// @ngInject
export default function ($lux, luxGridConfig) {
    
    luxGridConfig.registerDataProvider('rest', rest);
}
