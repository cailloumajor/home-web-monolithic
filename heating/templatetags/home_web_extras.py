# -*- coding: utf-8 -*-

from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def requirejs(entry_point_url, requirejs_url):
    debug_tag = """<script data-main="{data_main}" src="{src}"></script>"""
    prod_tag = """<script src="{src}"></script>"""
    if not settings.REQUIREJS_PROD:
        return debug_tag.format(data_main=entry_point_url, src=requirejs_url)
    else:
        return prod_tag.format(src=entry_point_url)
