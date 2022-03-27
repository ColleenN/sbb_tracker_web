from rest_framework import serializers

from apps.game_data.models import game as game_models
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

    class Meta:
        model = game_models.SBBGameCharacter
        fields = ('',)


class CombatSerializer(serializers.ModelSerializer):
    """
    For info on one round of combat from one player's POV.
    """

    class Meta:
        model = game_models.SBBGameTurn
        fields = ('')
        list_serializer_class = CombatListSerializer
