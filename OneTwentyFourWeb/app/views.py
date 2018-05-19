"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponse, Http404, JsonResponse
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import json

from app.models import Riding, PollAveragePoint

def main(request):
    riding_data = dict()
    for riding in Riding.objects.all():
        riding_obj = dict()
        riding_obj['results'] = riding.results
        riding_obj['percents'] = riding.percents
        riding_obj['swings'] = riding.swings
        riding_obj['name'] = riding.name
        riding_data[riding.riding_id] = riding_obj
    current_average = PollAveragePoint.objects.all().order_by('-date')[0]
    return render(request, 'app/main.html', context={'riding_data' : riding_data,
                                                     'poll_average' : current_average})