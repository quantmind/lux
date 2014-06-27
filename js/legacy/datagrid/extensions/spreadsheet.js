    
    DataGrid.Extension('spreadsheet', {
        
        columnLabel: function (index) {
            var dividend = index + 1,
                columnLabel = '',
                modulo;
            while (dividend > 0) {
                modulo = (dividend - 1) % 26;
                columnLabel = String.fromCharCode(65 + modulo) + columnLabel;
                dividend = parseInt((dividend - modulo) / 26, 10);
            }
            return columnLabel;
        }
    });