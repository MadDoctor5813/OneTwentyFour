"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponse, Http404, JsonResponse
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

from app.models import Riding, PartyResult

def main(request):
    return render(request, 'app/main.html')

def get_riding_data(request, riding_id=None):
    if riding_id is None:
        return HttpResponseBadRequest('Riding id required.')
    try:
        riding = Riding.objects.get(riding_id=riding_id)
    except ObjectDoesNotExist:
        raise Http404('Riding not found.')
    response_dict = dict()
    response_dict['name'] = riding.name
    response_dict['id'] = riding.riding_id
    results = dict()
    percents = dict()
    swings = dict()
    for result in riding.results.all():
        results[result.party] = result.vote_count
        percents[result.party] = result.percent
        swings[result.party] = result.swing
    response_dict['results'] = results
    response_dict['percents'] = percents
    response_dict['swings'] = swings
    return JsonResponse(response_dict)