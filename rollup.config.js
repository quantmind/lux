import json from 'rollup-plugin-json';
import babel from 'rollup-plugin-babel';
import nodeResolve from 'rollup-plugin-node-resolve';

export default {
    entry: 'lux/js/index.js',
    format: 'iife',
    moduleName: 'lux',
    plugins: [
        json(),
        babel({
            babelrc: false,
            presets: ['es2015-rollup']
        }),
        nodeResolve({jsnext: true})
    ],
    dest: 'build/rollup.js'
};
