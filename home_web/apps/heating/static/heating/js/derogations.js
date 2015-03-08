define(
    ['jquery', 'jquery-ui/button'],
function($) {
    return {
        init: function() {
            var self = this;
            $('#derogation-list').addClass(
                'ui-widget ui-widget-content ui-corner-all derogation-js'
            ).children('h2').addClass(
                'ui-widget-header ui-corner-all'
            ).children('a').button();
            this.arrange();
        },
        arrange: function() {
            $('#derogation-list .urls a').button();
            $(".derog-check:contains('X')").addClass('ui-icon ui-icon-check');
        },
        update: function() {
            var self = this;
            $('#derog-table-container').load('derogation/', self.arrange);
        },
    };
});
