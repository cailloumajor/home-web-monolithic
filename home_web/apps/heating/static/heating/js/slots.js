define(['jquery', 'app/consts', 'app/form', 'jcanvas'], 
       function($, CST, form) {

    function timeToScale(strTime) {
        var timeArray = strTime.split(':');
        var hours = parseInt(timeArray[0], 10);
        var minutes = parseInt(timeArray[1], 10);
        minutes = (minutes % 15 == 0) ? minutes : minutes + 1;
        if (minutes == 60) {
            hours += 1;
            minutes = 0;
        }
        return (hours + minutes / 60) * 4;
    }

    return {
        $can: null,
        groupName: '',
        delMode: function(set) {
            var $delInd = $('#del-ind');
            if (typeof(set) == 'boolean') {
                $delInd.toggleClass('hidden', !set);
                $('#del-btn').toggleClass('hidden', set);
            }
            return ($delInd.length > 0) && !$delInd.hasClass('hidden');
        },
        days: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
        init: function(zoneSlots) {
            this.$can = $(zoneSlots.id.replace('zone-slots', '#can'));
            var data = {
                pk: 'add', mode: 'add', start_time: '0:0', end_time: '24:0',
                mon: true, tue: true, wed: true, thu: true, fri: true, sat: true, sun: true,
                addUpdURL: $(zoneSlots).find('.create-url').attr('href'), delURL: '',
            };
            this.draw(data);
            var self = this;
            $(zoneSlots).find('.slot-desc').each(function() {
                data = {};
                data.pk = this.id;
                $(this).children('td:not(.urls)').each(function() {
                    data[this.className] = this.textContent;
                });
                data.addUpdURL = $(this).find('.edit-url').attr('href');
                data.delURL = $(this).find('.del-url').attr('href');
                self.draw(data);
            });
        },    
        draw: function(slotData) {
            var xstart = timeToScale(slotData.start_time) * CST.XSPACE + CST.X_ORI_SLOTS;
            var slotWidth = timeToScale(slotData.end_time) * CST.XSPACE - xstart + CST.X_ORI_SLOTS;  
            var self = this;
            for (var i=0; i<this.days.length; i++) {
                if (! slotData[this.days[i]]) continue;
                this.$can.drawRect({
                    strokeStyle: 'rgb(' + CST.SLOTS_REPR[slotData.mode][0] + ')',
                    strokeWidth: 0,
                    fillStyle: 'rgba(' + CST.SLOTS_REPR[slotData.mode][0] + ',0.3)',
                    x: xstart, y: CST.Y_ORI_SLOTS + CST.YSPACE * i,
                    width: slotWidth, height: CST.SLOTS_HEIGHT,
                    fromCenter: false,
                    layer: true,
                    groups: [slotData.pk],
                    data: {
                        addUpdURL: slotData.addUpdURL,
                        delURL: slotData.delURL,
                        slotsObj: self,
                    },
                    click: self.click,
                    mouseover: (slotData.pk != 'add') && function(layer) {
                        $(this).setLayerGroup(layer.groups[0], {
                            strokeWidth: 2,
                        });
                    },
                    mouseout: (slotData.pk != 'add') && function(layer) {
                        $(this).setLayerGroup(layer.groups[0], {
                            strokeWidth: 0,
                        });
                    },
                    cursors: {
                        mouseover: 'pointer',
                    },
                });
            }
        },
        click: function(layer) {
            var sl = layer.data.slotsObj;
            var callback;
            sl.$can = $(this);
            sl.groupName = layer.groups[0];
            if (!sl.delMode()) {
                callback = (sl.groupName == 'add') ? sl.draw : sl.update;
                form.load(layer.data.addUpdURL, callback, sl);
            } else if (sl.groupName != 'add') {
                callback = sl.del;
                form.load(layer.data.delURL, callback, sl);
            }
        },
        update: function(slotData) {
            this.del();
            this.draw(slotData);
        },
        del: function() {
            this.$can.removeLayerGroup(this.groupName).drawLayers();
            this.delMode(false);
        },
    };
});
