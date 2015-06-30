#-*- coding: utf-8 -*-

import datetime
import operator
from functools import reduce

from django import forms
from django.db.models import Q
from django.forms import widgets

from .models import Slot, Derogation

def validate_quarter_hour(value):
    if value.minute % 15 != 0:
        raise forms.ValidationError(
            "Seules les valeurs 00, 15, 30 et 45 sont autorisées pour les minutes"
        )

class OffsetTimeWidget(widgets.TimeInput):
    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.time):
            value = (
                datetime.datetime(1, 1, 1, value.hour, value.minute) +
                datetime.timedelta(minutes=1)
                ).time()
        return super(OffsetTimeWidget, self).render(name, value, attrs)

class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = [
            'zone', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
            'start_time', 'end_time', 'mode',
        ]
        widgets = {
            'zone': widgets.TextInput(attrs={'readonly':'true'}),
            'start_time': widgets.TimeInput(format='%H:%M'),
            'end_time': OffsetTimeWidget(format='%H:%M'),
            'mode': widgets.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(SlotForm, self).__init__(*args, **kwargs)
        self.fields['start_time'].validators += [validate_quarter_hour]
        self.fields['end_time'].validators += [validate_quarter_hour]
        self.fields['start_time'].input_formats = ['%H:%M']
        self.fields['end_time'].input_formats = ['%H:%M']
        
    def is_valid(self):
        valid = super(SlotForm, self).is_valid()
        for f in self.errors:
            if f != '__all__':
                self.fields[f].widget.attrs.update({'class': 'error'})
        return valid

    def clean_end_time(self):
        time = self.cleaned_data['end_time']
        dt = datetime.datetime(1, 1, 2, time.hour, time.minute) - \
             datetime.timedelta(minutes=1)
        return dt.time()

    def clean(self):
        cl_data = super(SlotForm, self).clean()
        days_on = [d for d in
                   ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
                   if cl_data.get(d)]
        q_objects = [Q(t) for t in [(d, True) for d in days_on]]
        s_time = cl_data.get('start_time')
        e_time = cl_data.get('end_time')
        zone = cl_data.get('zone')

        if not days_on:
            raise forms.ValidationError(
                "Aucun jour sélectionné"
            )

        if (s_time is not None) and (e_time is not None) and zone:
            if not s_time < e_time:
                raise forms.ValidationError(
                    "L'heure de fin doit être supérieure à l'heure de début"
                )
            elif Slot.objects.exclude(pk=self.instance.pk).filter(zone_id=zone).filter(
                    reduce(operator.or_, q_objects)).filter(
                    (Q(start_time__lte=s_time) & Q(end_time__gte=s_time)) | \
                    (Q(start_time__lte=e_time) & Q(end_time__gte=e_time)) | \
                    (Q(start_time__gte=s_time) & Q(end_time__lte=e_time))
            ).exists():
                raise forms.ValidationError(
                    "Les horaires sont en conflit avec un créneau existant"
                )

        return cl_data

class HiddenDateTimeWidget(widgets.DateTimeInput):
    input_type = 'hidden'

class DerogationForm(forms.ModelForm):

    start_initial = forms.DateTimeField(
        widget = HiddenDateTimeWidget(format="%d/%m/%Y %H:%M"),
        required = False
    )

    class Meta():
        model = Derogation
        fields = ['start_initial', 'zones', 'start_dt', 'end_dt', 'mode']
        widgets = {
            'start_dt': widgets.DateTimeInput(format="%d/%m/%Y %H:%M"),
            'end_dt': widgets.DateTimeInput(format="%d/%m/%Y %H:%M"),
            'mode': widgets.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(DerogationForm, self).__init__(*args, **kwargs)
        self.fields['start_dt'].input_formats = ["%d/%m/%Y %H:%M"]
        self.fields['end_dt'].input_formats = ["%d/%m/%Y %H:%M"]
        self.fields['end_dt'].validators += [validate_quarter_hour]
