import json from 'rollup-plugin-json';
import babel from 'rollup-plugin-babel';
import nodeResolve from 'rollup-plugin-node-resolve';
import replace from 'rollup-plugin-replace';
import commonjs from 'rollup-plugin-commonjs';

export default {
    entry: 'lux/js/index.js',
    format: 'iife',
    moduleName: 'lux',
    plugins: [
        json(),
        replace({
            "from 'lodash'": "from '../ld'"
        }),
        babel({
            babelrc: false,
            presets: ['es2015-loose-rollup']
        }),
        nodeResolve({
            jsnext: true,
            skip: ['angular']
        }),
        commonjs({
            include: [
                'node_modules/angular/**'
            ]
        })
    ],
    dest: 'build/rollup.js'
};
