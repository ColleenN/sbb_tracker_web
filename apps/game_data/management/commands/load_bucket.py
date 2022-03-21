from io import BytesIO
import json
import requests
import tarfile

from django.core.management.base import BaseCommand

from apps.game_data.serializers.game import GameTarSerializer
from apps.game_data.models.game import SBBGame


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

            # TODO Check for standard AWS error message XML
            file_stream = BytesIO(response.raw.read())
            with tarfile.open(mode='r:gz', fileobj=file_stream) as tarball:
                for tarblock in tarball.getmembers():
                    as_file = tarball.extractfile(tarblock)
                    data = json.load(as_file)

                    serializer = GameTarSerializer(data=data)

                    uuid = tarblock.name.split('/')[1][:-5]
                    in_db = SBBGame.objects.filter(uuid=uuid)
                    if in_db.exists():
                        serializer.instance = in_db.first()
                        serializer.partial = True

                    if serializer.is_valid():
                        serializer.save()
                    else:
                        # TODO set up some real logging
                        print(tarblock.name)
                        print(serializer.errors)
