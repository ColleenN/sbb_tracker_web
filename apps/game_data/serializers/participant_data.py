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

    def validate(self, attrs):

        if not self.parent and 'match' not in attrs:
            raise serializers.ValidationError(
                {'match': 'Match required if no parent.'})
        return attrs

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

    def update(self, validated_data, instance):
        if 'player_id' in validated_data:
            player_obj, _ = meta_models.SBBPlayer.objects.get_or_create(
            account_id=validated_data['player_id'])
            instance.player = player_obj
        if 'match' in validated_data:
            instance.match = validated_data['match']
        if 'placement' in validated_data:
            instance.placement = validated_data['placement']

        instance.save()

        turn_data = zip(
            validated_data.pop('healths'),
            validated_data.pop('xps'),
            validated_data.pop('heroes')
        )
        turn_num = 1
        for hp, xp, hero in turn_data:
            self.update_turn(instance, turn_num, hp, xp, hero)
            turn_num = turn_num + 1

        return instance

    def create(self, validated_data):
        player_obj, _ = meta_models.SBBPlayer.objects.get_or_create(
            account_id=validated_data['player_id'])
        validated_data['player'] = player_obj
        del validated_data['player_id']

        instance = game_models.SBBGameParticipant.objects.create(
            match=validated_data['match'], player=player_obj)

        del validated_data['match']

        return self.update(validated_data, instance)

    class Meta:
        model = game_models.SBBGameParticipant
        fields = ('player_id', 'healths', 'xps', 'heroes', 'match')
        extra_kwargs = {'match': {'required': False}}
