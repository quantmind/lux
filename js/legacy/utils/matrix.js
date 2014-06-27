(function () {
    function matrix (_rows, _cols) {
        var _size, m, i, j, mat;
        // _rows could be an array
        if (_rows === undefined || _rows === null) {
            _rows = 0;
        }
        if (typeof(_rows) === Number) {
            if(_rows < 0) {
                _rows = 0;
            }
            _cols = _cols || 1;
        }
        _size = _rows * _cols;
        // Do size checks
        m = new Float32Array(_size);
        if (mat) {
            for (i = 0; i < _size; i++) {
                m[i] = mat[i];
            }
        }
        //
        return {
            constructor: matrix,
            vector: function () {
                return m;
            },
            rows: function () {
                return _rows;
            },
            cols: function () {
                return _cols;
            },
            size: function () {
                return _size;
            },
            set: function (i, j, value) {
                var k = _rows*i + j;
                if (k >= 0 && k < _size) {
                    m[k] = value + 0; 
                }
            },
            get: function (i, j) {
                var k = _rows*i + j;
                if (k >= 0 && k < _size) {
                    return m[k]; 
                }
            },
            forEach: function (callback) {
                for (i = 0; i < _rows; i++) {
                    for (j = 0; j < _cols; j++) {
                        callback(i, j, m[_rows*i + j]);
                    }
                }
            },
            clone: function () {
                this.constructor(this);
            }
        };  
    }
    // 3x3 algebra
    function matrix3 (m3) {
        var base = matrix(3, 3);
        //
        function _inverse(m, det_only) {
            var a00 =   m[4] * m[8] - m[5] * m[7],
                a01 =   m[3] * m[8] - m[5] * m[6],
                a02 =   m[3] * m[7] - m[4] * m[5],
                det = m[0] * a00 - m[1] * a01 + m[2] * a02;
            if (det_only) {
                return det;
            } else {
                if (det === 0) {
                    logger.warn('Singular matrix, cannot invert');
                } else {
                    var a10 = m[1] * m[8] - m[2] * m[7],
                        a11 = m[0] * m[8] - m[2] * m[6],
                        a12 = m[0] * m[7] - m[1] * m[6],
                        a20 = m[1] * m[5] - m[2] * m[4],
                        a21 = m[0] * m[5] - m[2] * m[3],
                        a22 = m[0] * m[4] - m[1] * m[3],
                        idet = 1.0 / det;
                    m[0] = idet * a00;
                    m[1] =-idet * a01;
                    m[2] = idet * a02;
                    m[3] =-idet * a10;
                    m[4] = idet * a11;
                    m[5] =-idet * a12;
                    m[6] = idet * a20;
                    m[7] =-idet * a21;
                    m[8] = idet * a22;
                }
            }
        }
        //
        return $.extend({}, base, {
            constructor: matrix3,
            transapose: function () {
                var m = this.vector(),
                    tmp;
                tmp = m[1]; m[1] = m[3]; m[3] = tmp;
                tmp = m[2]; m[2] = m[6]; m[6] = tmp;
                tmp = m[5]; m[5] = m[7]; m[7] = tmp;
                return this;
            },
            det: function () {
                return _inverse(this.vector(), true);
            },
            inverse: function () {
                _inverse(this.vector());
                return this;
            },
            cross: function (_rhs) {
                var lhs = this.vector(),
                    rhs = _rhs.vector(),
                    m = this.constructor(),
                    v = m.vector();
                v[0] = lhs[0]*rhs[0] + lhs[1]*rhs[3] + lhs[2]*rhs[6];
                v[1] = lhs[0]*rhs[1] + lhs[1]*rhs[4] + lhs[2]*rhs[7];
                v[2] = lhs[0]*rhs[2] + lhs[1]*rhs[5] + lhs[2]*rhs[8];
                v[3] = lhs[3]*rhs[0] + lhs[4]*rhs[3] + lhs[5]*rhs[6];
                v[4] = lhs[3]*rhs[1] + lhs[4]*rhs[4] + lhs[5]*rhs[7];
                v[5] = lhs[3]*rhs[2] + lhs[4]*rhs[5] + lhs[5]*rhs[8];
                v[6] = lhs[6]*rhs[0] + lhs[7]*rhs[3] + lhs[8]*rhs[6];
                v[7] = lhs[6]*rhs[1] + lhs[7]*rhs[4] + lhs[8]*rhs[7];
                v[8] = lhs[6]*rhs[2] + lhs[7]*rhs[5] + lhs[8]*rhs[8];
                return m;
            }
        });
    }
    //
    math.matrix = matrix;
    math.matrix3 = matrix3;
}());