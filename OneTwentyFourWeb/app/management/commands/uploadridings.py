from django.core.management.base import BaseCommand
from app.models import Riding
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
            for riding in data:
                Riding.objects.create(riding_id=riding['id'],
                              name=riding['name'],
                              results=riding['results'],
                              percents=riding['percents'],
                              swings=riding['swings'])