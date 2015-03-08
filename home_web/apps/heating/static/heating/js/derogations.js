define(
    ['jquery', 'jquery-ui/button'],
function($) {
    return {
        init: function() {
            $('#derogation-list').addClass(
                'ui-widget ui-widget-content ui-corner-all derogation-js'
            ).children('h2').addClass(
                'ui-widget-header ui-corner-all'
            ).children('a').button();
            $('#derogation-list .urls a').button();
            $(".derog-check:contains('X')").addClass('ui-icon ui-icon-check');
        },
    };
});
