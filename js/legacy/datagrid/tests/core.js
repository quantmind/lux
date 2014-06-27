module('lux.datagrid');

test("object", function() {
    equal(typeof(lux.DataGrid), 'function', 'DataGrid meta tests');
    equal(typeof(lux.DataGrid.prototype), 'object');    
});
