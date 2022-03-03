from datetime import datetime
import requests

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    # TODO - make this pull from an setting/env var
    url_root = 'https://9n2ntsouxb.execute-api.us-east-1.amazonaws.com/prod/api/v1/data/daily-rollup'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('date', nargs='?')

    def handle(self, *args, **options):

        file_name = f"{options['date']}.tar.gz"

        response = requests.get(
            url=f"{self.url_root}/{file_name}",
            stream=True
        )

        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(response.raw.read())

