var requirejs = require('requirejs');

var configs = [
    // heating application module optimization (all in one file)
    {
        baseUrl: 'home_web/js/heating',
        mainConfigFile: 'home_web/js/heating/zone_list.js',
        wrapShim: true,
        optimize: 'uglify2',
        name: 'zone_list',
        include: ['../../bower/requirejs/require'],
        out: '../build/home_web/js/heating/zone_list.js',
    },
    // heating application css optimization (all in one file)
    {
        cssIn: 'home_web/css/heating/zone_list.css',
        out: '../build/home_web/css/heating/zone_list.css',
        optimizeCss: 'standard.keepComments',
    },
    // other static files related to the project
    {
        appDir: 'home_web',
        dir: '../build/home_web/',
        optimize: 'uglify2',
        optimizeCss: 'standard.keepComments',
        fileExclusionRegExp: /^(?:bower|heating|jquery-ui\.css)$/,
        keepBuildDir: true,
    },
];

process.chdir(process.argv[2]);

configs.forEach(function (config, index, array) {
    config.logLevel = 0;
    requirejs.optimize(config, function (buildResponse) {
        // noop
    }, function (error) {
        console.error(error.toString());
        process.exit(1);
    });
});
