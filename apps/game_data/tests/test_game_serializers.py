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
from apps.game_data.serializers.meta import (
    GamePieceSerializer
)
from apps.game_data.serializers.participant_data import (
    PlayerGameRecordSerializer
)
from apps.game_data.serializers.combat_data import CombatSerializer


class TestSerializers(TestCase):

    def setUp(self) -> None:
        self.samples_dir = 'apps/game_data/tests/json_samples'

        json_data = json.load(
            open(os.path.join(self.samples_dir, 'meta_sample.json'), 'r'))
        serializer = GamePieceSerializer(data=json_data, many=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

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

    def test_singleton_combat_serializer(self):
        # Set up all the stuff that would be passed/spec'ed by context
        match_obj = game_models.SBBGame.objects.create(uuid=uuid4())
        player_1 = meta_models.SBBPlayer.objects.create(
            account_id="61F59D54CA111EB2")
        participant_1 = game_models.SBBGameParticipant.objects.create(
            match=match_obj, player=player_1)
        turn_obj_1 = game_models.SBBGameTurn(
            turn_num=12, participant=participant_1)

        json_data = json.load(
            open(
                os.path.join(self.samples_dir, 'singleton_combat_sample.json'),
                'r'
            )
        )
        serializer = CombatSerializer(
            data=json_data, context={'match': match_obj, 'round': 12})
        print(serializer.is_valid())
        print(serializer.errors)
        self.fail()

    def test_combat_serializer(self):

        # Set up all the stuff that would be passed/spec'ed by context
        match_obj = game_models.SBBGame.objects.create(uuid=uuid4())
        player_1 = meta_models.SBBPlayer.objects.create(
            account_id="61F59D54CA111EB2")
        participant_1 = game_models.SBBGameParticipant.objects.create(
            match=match_obj, player=player_1)
        turn_obj_1 = game_models.SBBGameTurn(
            turn_num=12, participant=participant_1)
        player_2 = meta_models.SBBPlayer.objects.create(
            account_id="F52948771128A2F6")
        participant_2 = game_models.SBBGameParticipant.objects.create(
            match=match_obj, player=player_2)
        turn_obj_2 = game_models.SBBGameTurn(
            turn_num=12, participant=participant_2)

        json_data = json.load(
            open(
                os.path.join(self.samples_dir, 'combat_sample.json'),
                'r'
            )
        )
        serializer = CombatSerializer(
            data=json_data, context={'match': match_obj}, many=True)

        print(serializer.is_valid())
        print(serializer.errors)
        print(serializer.data)
        self.fail()
