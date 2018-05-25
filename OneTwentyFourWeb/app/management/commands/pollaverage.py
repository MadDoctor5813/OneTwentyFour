from django.core.management.base import BaseCommand
from app.models import Poll, PollAveragePoint
import os

POLLS_TO_AVERAGE = 6

class Command(BaseCommand):

    def handle(self, *args, **options):
        polls = list(Poll.objects.all().order_by('-date, -pk'))
        PollAveragePoint.objects.all().delete()
        #generate an average point for each poll
        for idx in range(len(polls)):
            #just a simple moving average for now
            average = dict()
            polls_used = 0
            for i in range(POLLS_TO_AVERAGE):
                try:
                    poll = polls[idx - i]
                except IndexError:
                    #if we go beyond the beginning of the array just break the loop
                    break
                for party, result in poll.results.items():
                    if average.get(party) is None:
                        average[party] = 0
                    average[party] += result
                polls_used += 1
            for party, result in average.items():
                average[party] = average[party] / polls_used
            PollAveragePoint.objects.create(current=average, date=polls[idx].date)