import json

from django.core.management.base import BaseCommand

from apps.game_data.serializers.meta import GamePieceSerializer


class Command(BaseCommand):

    url_root = 'https://9n2ntsouxb.execute-api.us-east-1.amazonaws.com/prod/api/v1/data/daily-rollup'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('path', nargs='?')

    def handle(self, *args, **options):

        # Run w/ ./apps/game_data/tests/json_samples/meta_sample.json
        # Until raschy gets an auto-refreshing bucket up
        json_data = json.load(open(options['path'], 'r'))
        serializer = GamePieceSerializer(data=json_data, many=True)

        if serializer.is_valid():
            objs = serializer.save()
            print(f'{len(objs)} records created.')
        else:
            print(f'Data invalid - {serializer.errors}')
