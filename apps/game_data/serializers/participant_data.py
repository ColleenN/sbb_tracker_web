from rest_framework import serializers

from apps.game_data.models import (meta as meta_models, game as game_models)
from apps.game_data.serializers.utils import (
    IDKeyListField,
    JSONDashConvertMixin
)
from apps.game_data.serializers.validators import XPStringValidator


class PlayerGameRecordSerializer(
    JSONDashConvertMixin,
    serializers.ModelSerializer
):
    """
    Processes JSON subfield containing a game "summary" for player.
    """

    player_id = serializers.CharField()
    healths = IDKeyListField(
        zero_biased=False, child=serializers.IntegerField()
    )
    xps = IDKeyListField(
        zero_biased=False,
        child=serializers.CharField(
            max_length=8, validators=[XPStringValidator()])
    )
    heroes = serializers.ListSerializer(
        child=serializers.CharField(max_length=16)
    )

    def update_turn(self, instance, turn_num, hp, xp, hero):
        """Update Turn data object associated with participant instance."""
        turn_obj, _ = game_models.SBBGameTurn.objects.get_or_create(
            participant=instance, turn_num=turn_num)
        hero_obj, _ = meta_models.SBBHero.objects.get_or_create(
            template_id=hero
        )
        turn_obj.hero = hero_obj
        turn_obj.hp = hp

        level, fraction = xp.split('.')
        turn_obj.level = level
        turn_obj.exp = fraction

        turn_obj.save()

        return turn_obj

    def create(self, validated_data):
        validated_data['match'] = self.context['match']

        player_obj, _ = meta_models.SBBPlayer.objects.get_or_create(
            account_id=validated_data['player_id'])
        validated_data['player'] = player_obj
        del validated_data['player_id']

        turn_data = zip(
            validated_data.pop('healths'),
            validated_data.pop('xps'),
            validated_data.pop('heroes')
        )

        participant_obj = super().create(validated_data)

        turn_num = 1
        for hp, xp, hero in turn_data:
            self.update_turn(participant_obj, turn_num, hp, xp, hero)
            turn_num = turn_num + 1

        return participant_obj

    class Meta:
        model = game_models.SBBGameParticipant
        fields = ('player_id', 'healths', 'xps', 'heroes')
