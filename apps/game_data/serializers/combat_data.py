from rest_framework import serializers

from apps.game_data.models import (
    game as game_models,
    meta as meta_models
)
from apps.game_data.serializers.utils import IDKeyListSerializer


class CombatListSerializer(IDKeyListSerializer):
    """
    Slightly tweaked version of IDKey util that shunts round number into
    serializer context.
    """

    def to_internal_value(self, data):
        round_num = data.pop('round', None)
        self.child.context['round'] = round_num
        return super().to_internal_value(data)


class GameCharacterSerializer(serializers.ModelSerializer):

    id = serializers.SlugRelatedField(
        slug_field='template_id',
        queryset=meta_models.SBBCharacter.objects.all(),
        source='base_character'
    )

    class Meta:
        model = game_models.SBBGameCharacter
        fields = ('id', 'attack', 'health', 'golden', 'position')


class CombatSerializer(serializers.ModelSerializer):
    """
    For info on one round of combat from one player's POV.
    """

    treasures = serializers.SlugRelatedField(
        slug_field='template_id',
        queryset=meta_models.SBBTreasure.objects.all(),
        many=True
    )
    spells = serializers.SlugRelatedField(
        slug_field='template_id',
        queryset=meta_models.SBBSpell.objects.all(),
        many=True
    )
    characters = GameCharacterSerializer(many=True)

    class Meta:
        model = game_models.SBBGameTurn
        fields = ('characters', 'spells', 'treasures')
        list_serializer_class = CombatListSerializer
