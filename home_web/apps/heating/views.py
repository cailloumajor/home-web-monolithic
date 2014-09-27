#-*- coding: utf-8 -*-

import json
import datetime

from django.shortcuts import render
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse

from .models import Slot, Zone
from .forms import SlotForm

class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.time):
            return obj.strftime('%H:%M')
        return json.JSONEncoder.default(self, obj)

class AjaxResponseMixin(object):
    def render_to_json_response(self, context):
        data = json.dumps(context, cls=ExtendedEncoder)
        return HttpResponse(data, content_type='application/json')

    def form_valid(self, form):
        response = super(AjaxResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = model_to_dict(self.object)
            data['django_success'] = True
            data['pk'] = 'pk-%s' % self.object.pk
            data['addUpdURL'] = reverse('update_slot', kwargs={'pk':self.object.pk})
            data['delURL'] = reverse('del_slot', kwargs={'pk':self.object.pk})
            return self.render_to_json_response(data)
        else:
            return response

    def form_invalid(self, form):
        response = super(AjaxResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors)
        else:
            return response

    def delete(self, request, *args, **kwargs):
        response = super(AjaxResponseMixin, self).delete(request, *args, **kwargs)
        if request.is_ajax():
            return self.render_to_json_response({'django_success':True})
        else:
            return response

class ZoneList(ListView):
    model = Zone

class SlotCreate(AjaxResponseMixin, CreateView):
    model = Slot
    form_class = SlotForm
    success_url = reverse_lazy('zone_list')
    
    def get_initial(self):
        initial = super(SlotCreate, self).get_initial()
        initial = initial.copy()
        initial['zone'] = self.kwargs.get('zone')
        return initial

class SlotUpdate(AjaxResponseMixin, UpdateView):
    model = Slot
    form_class = SlotForm
    success_url = reverse_lazy('zone_list')

class SlotDelete(AjaxResponseMixin, DeleteView):
    model = Slot
    success_url = reverse_lazy('zone_list')

class ModeAPI(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        def validate_request(url_params):
            param_cond = {
                'd': (1, 7),
                'h': (0, 23),
                'm': (0, 59)
            }
            err = []
            if not all(key in url_params for key in param_cond):
                err.append({
                    'text': ("One or more parameters missing in the URL. "
                             "Required: d, h & m"),
                    })
                return err
            for key in param_cond:
                mini = param_cond[key][0]
                maxi = param_cond[key][1]
                try:
                    int_val = int(url_params[key])
                except ValueError:
                    err.append({
                        'text': ("Conversion of '%s' parameter "
                                 "to integer failed") % key
                    })
                    continue
                if not (mini <= int_val <= maxi):
                    err.append({
                        'text': ("'%s' URL parameter "
                                 "out of range (%s-%s)") % (key, mini, maxi)
                    })
            return err
        errors = validate_request(request.GET)
        data = {}
        if errors:
            data['errors'] = errors
            return HttpResponse(json.dumps(data),
                                content_type='application/json',
                                status=400)
        modes = {}
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        day = days[int(request.GET['d']) - 1]
        time = datetime.time(
            hour=int(request.GET['h']),
            minute=int(request.GET['m'])
        )
        for zone in Zone.objects.all():
            try:
                modes[zone.num] = zone.slot_set.filter(**{day: True}).get(
                    start_time__lte = time, end_time__gte = time
                ).mode
            except:
                modes[zone.num] = 'C'
        data['modes'] = modes
        return HttpResponse(json.dumps(data), content_type='application/json')
