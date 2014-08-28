#-*- coding: utf-8 -*-

import json
import datetime

from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
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
