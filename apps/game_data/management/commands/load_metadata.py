import requests

from django.core.management.base import BaseCommand

from apps.game_data.serializers.game import GameTarSerializer
from apps.game_data.models.game import SBBGame


class Command(BaseCommand):

    url_root = 'https://9n2ntsouxb.execute-api.us-east-1.amazonaws.com/prod/api/v1/data/daily-rollup'

    def handle(self, *args, **options):

        response = requests.get(
            url=f"{self.url_root}/schema.txt",
            stream=True
        )

        print(response.status_code)
        print(response.json())
