from uuid import uuid4
import json
import os

from django.test import TestCase

from apps.game_data.models import (
    game as game_models,
    meta as meta_models
)
from apps.game_data.serializers.game import (
    GameTarSerializer
)
from apps.game_data.serializers.participant_data import (
    PlayerGameRecordSerializer
)


class TestSerializers(TestCase):

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

        self.assertEqual(meta_models.SBBPlayer.objects.all().count(), 8)
        main_player = meta_models.SBBPlayer.objects.get(
            account_id="61F59D54CA111EB2")

        participant_obj = main_player.sbbgameparticipant_set
        self.assertEqual(participant_obj.all().count(), 1)
        self.assertEqual(participant_obj.first().placement, 5)

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

        heroes = meta_models.SBBHero.objects.all()
        self.assertEqual(heroes.count(), 1)
        self.assertEqual(heroes.first().template_id, 80)

        turns = game_models.SBBGameTurn.objects.all()
        self.assertEqual(turns.count(), 12)

        first_turn = turns.first()
        self.assertEqual(first_turn.hero, heroes.first())
        self.assertEqual(first_turn.level, 2)
        self.assertEqual(first_turn.exp, 0)
        self.assertEqual(first_turn.hp, 40)

        last_turn = turns.last()
        self.assertEqual(last_turn.hero, heroes.first())
        self.assertEqual(last_turn.level, 6)
        self.assertEqual(last_turn.exp, 0)
        self.assertEqual(last_turn.hp, -2)
