from uuid import uuid4
import json
import os

from django.test import TestCase

from apps.game_data.models import game as game_models
from apps.game_data.serializers.game import (
    GameTarSerializer,
    PlayerGameRecordSerializer
)


class TestSample(TestCase):

    def setUp(self) -> None:
        self.samples_dir = 'apps/game_data/tests/json_samples'

    def test_main_serializer(self):

        json_data = json.load(
            open(os.path.join(self.samples_dir, 'full_sample.json'), 'r'))
        serializer = GameTarSerializer(data=json_data)
        self.assertTrue(serializer.is_valid())
        obj = serializer.save()
        self.assertEqual(
            str(obj.uuid),
            'b822d294-38ce-4696-ab38-d286f2e91b1e'
        )
        self.fail()

    def test_player_serializer(self):

        match_obj = game_models.SBBGame.objects.create(uuid=uuid4())
        json_data = json.load(
            open(os.path.join(self.samples_dir, 'player_sample.json'), 'r'))
        serializer = PlayerGameRecordSerializer(
            data=json_data, context={'match': match_obj})

        self.assertTrue(serializer.is_valid())
        serializer.save()

        game_players = game_models.SBBGameParticipant.objects.all()
        self.assertEqual(game_players.count(), 1)

        participant = game_players.first()
        self.assertEqual(participant.player.account_id, "94EFFF42C8A8A56E")

        self.fail()