# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.test import  TestCase
from django.core.urlresolvers import reverse

from ..models import Zone, Slot

class SlotFormTest(TestCase):

    longMessage = True

    _url = reverse('new_slot', kwargs={'zone':1})
    _req_field_error = "Ce champ est obligatoire."
    _no_day_sel_error = "Aucun jour sélectionné"
    _et_greater_error = "L'heure de fin doit être supérieure à l'heure de début"
    _conflict_error = "Les horaires sont en conflit avec un créneau existant"
    _quar_hour_error = ("Seules les valeurs 00, 15, 30 et 45 "
                        "sont autorisées pour les minutes")

    def setUp(self):
        z = Zone.objects.create(num=1, desc="Test zone")
        Slot.objects.create(
            zone=z, mon=True, mode='E',
            start_time=datetime.time(10),
            end_time=datetime.time(13,59)
        )

    def test_required_fields(self):
        response = self.client.post(self._url)
        self.assertFormError(response, 'form', 'start_time',
                             self._req_field_error)
        self.assertFormError(response, 'form', 'end_time',
                             self._req_field_error)
        self.assertFormError(response, 'form', 'mode',
                             self._req_field_error)

    def test_no_day_selected(self):
        response = self.client.post(self._url)
        self.assertFormError(response, 'form', None, self._no_day_sel_error)
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            response = self.client.post(self._url, {day:True})
            self.assertNotIn(
                self._no_day_sel_error,
                response.context['form'].errors.get('__all__', []),
                msg="Field: '{}'".format(day)
            )

    def test_end_time_greater_than_start_time(self):
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'04:30', 'end_time':'04:15'}
        )
        self.assertFormError(response, 'form', None, self._et_greater_error)
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'04:30', 'end_time':'04:45'}
        )
        self.assertNotIn(
            self._et_greater_error,
            response.context['form'].errors.get('__all__', [])
        )

    def test_conflict_start_time_in_other_slot(self):
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'13:45', 'end_time':'15:00'}
        )
        self.assertFormError(response, 'form', None, self._conflict_error)

    def test_conflict_end_time_in_other_slot(self):
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'08:00', 'end_time':'10:15'}
        )
        self.assertFormError(response, 'form', None, self._conflict_error)

    def test_conflict_start_time_and_end_time_in_other_slot(self):
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'10:15', 'end_time':'13:45'}
        )
        self.assertFormError(response, 'form', None, self._conflict_error)

    def test_quarter_hour(self):
        for fld in ['start_time', 'end_time']:
            response = self.client.post(self._url, {fld:'01:03'})
            self.assertFormError(response, 'form', fld, self._quar_hour_error)
            for minutes in ['00', '15', '30', '45']:
                response = self.client.post(self._url,
                                            {fld:'01:{}'.format(minutes)})
                self.assertNotIn(
                    self._quar_hour_error,
                    response.context['form'].errors.get(fld, []),
                    msg="Field: '{}', minutes: '{}'".format(fld, minutes)
                )

    def test_form_valid(self):
        self.assertEqual(Slot.objects.filter(zone__num=1).count(), 1)
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            response = self.client.post(
                self._url,
                {
                    'zone': 1,
                    day: True,
                    'start_time': '04:30',
                    'end_time': '09:45',
                    'mode': 'E'
                }
            )
            self.assertRedirects(response, reverse('zone_list'))
        self.assertEqual(Slot.objects.filter(zone__num=1).count(), 8)
