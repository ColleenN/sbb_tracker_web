import json
import os

from django.test import TestCase

from apps.game_data.models.meta import (
    SBBCharacter,
    SBBHero,
    SBBSpell,
    SBBTreasure
)
from apps.game_data.serializers.meta import GamePieceSerializer


class TestSerializers(TestCase):

    def setUp(self) -> None:
        self.samples_dir = 'apps/game_data/tests/json_samples'

    def test_one_json(self):
        """Test that we're reading an individual JSON as expected."""

        context = {'key': '0'}
        data = {
            "Id": "SBB_CHARACTER_FROGPRINCE",
            "Name": "Frog Prince"
        }
        serializer = GamePieceSerializer(context=context, data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.name, 'Frog Prince')
        self.assertEqual(instance.template_id, '0')
        self.assertEqual(instance.slug, 'SBB_CHARACTER_FROGPRINCE')

    def test_json_file(self):

        json_data = json.load(
            open(os.path.join(self.samples_dir, 'meta_sample.json'), 'r'))

        serializer = GamePieceSerializer(data=json_data, many=True)

        self.assertTrue(serializer.is_valid())
        objs = serializer.save()
        self.assertEqual(len(objs), 260)

        print(SBBCharacter.objects.all().count())
        print(SBBHero.objects.all().count())
        print(SBBSpell.objects.all().count())
        print(SBBTreasure.objects.all().count())

        self.fail()
