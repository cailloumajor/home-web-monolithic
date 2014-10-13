define(['jquery', 'jquery-ui-timepicker', 'jquery-ui/dialog'],
       function($) {
    return {
        $that: null,
        callback: null,
        load: function(url, callback) {
            var self = this;
            this.callback = callback;
            $('#form-container').load(url, function(response, status, jqxhr) {
                if (status != 'success') {
                    alert('Erreur de chargement du formulaire : ' + jqxhr.status + ' ' + jqxhr.statusText);
                } else {
                    self.$that = $(this).find('form');
                    self.init();
                }
            });
        },
        init: function() {
            var dialogTitle, dialogWidth;
            var self = this;
            switch (this.$that.attr('id')) {
            case 'slot-form':
                dialogTitle = 'Ajout / modification de créneau';
                dialogWidth = 560;
                $('#mode-choices label').unwrap().unwrap().each(function() {
                    $(this).before($(this).children('input'));
                });
                $('#days, #mode-choices').buttonset();
                $('#id_start_time, #id_end_time').attr('readonly', 'true').timepicker({
                    showPeriodLabels: false,
                    defaultTime: '',
                    hourText: 'Heures',
                    minuteText: 'Min.',
                    myPosition: 'center top',
                    atPosition: 'center bottom',
                    minutes: {interval: 15},
                });
                break;
            case 'slot-del-form':
                dialogTitle = 'Suppression de créneau';
                dialogWidth = 300;
                $('#cancel-anchor').remove();
                $('#slot-del-form h2').addClass("ui-widget ui-state-highlight ui-corner-all");
                break;
            }
            $('<input>', {
                'class': 'form-btn',
                type: 'button',
                value: 'Annuler',
                click: function() {
                    self.$that.remove();
                },
            }).insertAfter('input[type="submit"]');
            this.$that.dialog({
                closeOnEscape: false,
                dialogClass: 'no-close',
                draggable: false,
                modal: true,
                resizable: false,
                title: dialogTitle,
                width: dialogWidth,
            });
            $('.form-btn').button();
            this.$that.submit(this.submit);
        },   
        submit: function(event) {
            event.preventDefault();
            $.post(this.$that.attr('action'), this.$that.serialize(), this.success).fail(this.fail);
        },
        success: function(data, textStatus, jqXHR) {
            if (data.django_success) {
                this.$that.remove();
                this.callback(data);
            } else {
                this.$that.find('.errorlist').remove();
                var errors = data;
                for (var elist in errors) {
                    var $ul = $('<ul>', {'class':'errorlist'});
                    for (var e in errors[elist]) {
                        $('<li>', {text:errors[elist][e]}).appendTo($ul);
                    }
                    switch (elist) {
                    case '__all__':
                        $ul.prependTo(form.$that);
                        break;
                    case 'start_time':
                    case 'end_time':
                        $ul.appendTo('#times');
                        break;
                    case 'mode':
                        $ul.appendTo('#mode');
                        break;
                    }
                }
            }
        },
        fail: function(jqXHR, textStatus, errorThrown) {
            alert('Erreur de la requête : ' + textStatus + ' ' + errorThrown);
        },
    };
});
