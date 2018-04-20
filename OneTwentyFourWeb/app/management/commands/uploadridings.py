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
            for riding in data:
                riding_model = Riding()
                riding_model.name = riding['name']
                riding_model.riding_id = riding['id']
                results = riding['results']
                riding_model.result_lib = results['LIB']
                riding_model.result_pc = results['PC']
                riding_model.result_ndp = results['NDP']
                riding_model.result_oth = results['OTH']
                swings = riding['swings']
                riding_model.swing_lib = swings['LIB']
                riding_model.swing_pc = swings['PC']
                riding_model.swing_ndp = swings['NDP']
                riding_model.swing_oth = swings['OTH']
                percents = riding['percents']
                riding_model.percent_lib = percents['LIB']
                riding_model.percent_pc = percents['PC']
                riding_model.percent_ndp = percents['NDP']
                riding_model.percent_oth = percents['OTH']
                riding_model.save()