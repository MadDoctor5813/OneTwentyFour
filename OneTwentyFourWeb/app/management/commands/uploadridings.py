from django.core.management.base import BaseCommand
from app.models import Riding, PartyResult
import json
import os

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ridings_file')

    def handle(self, *args, **options):
        file_name = options['ridings_file']
        with open(file_name, 'r') as ridings_file:
            content = ridings_file.read()
            data = json.loads(content)
            Riding.objects.all().delete()
            PartyResult.objects.all().delete()
            for riding in data:
                riding_model = Riding()
                riding_model.name = riding['name']
                riding_model.riding_id = riding['id']
                riding_model.save()
                for party_name, _ in PartyResult.PARTY_CHOICES:
                    riding_model.results.create(
                        party=party_name,
                        vote_count=riding['results'][party_name],
                        percent=riding['percents'][party_name],
                        swing=riding['swings'][party_name]
                    )