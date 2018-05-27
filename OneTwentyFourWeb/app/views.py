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
from app.projection import Projection, project

def main(request):
    riding_data = dict()
    averages = list(PollAveragePoint.objects.all().order_by('-date', '-pk'))
    past_polls = list()
    for average in averages:
        past_polls.append({ 'current' : average.current, 'date' : str(average.date) })
    current_average = averages[0]
    all_ridings = Riding.objects.all()
    projection = project(all_ridings, current_average)
    for riding in all_ridings:
        riding_obj = dict()
        riding_obj['results'] = riding.results
        riding_obj['percents'] = riding.percents
        riding_obj['swings'] = riding.swings
        riding_obj['name'] = riding.name
        riding_obj['projected'] = projection.riding_projections[riding.riding_id]
        riding_data[riding.riding_id] = riding_obj
    return render(request, 'app/main.html', context={'riding_data' : riding_data,
                                                     'current_average' : current_average,
                                                     'past_polls' : json.dumps(past_polls),
                                                     'projection' : projection})

def methodology(request):
    return render(request, 'app/methodology.html')

def contact(request):
    return render(request, 'app/contact.html')
