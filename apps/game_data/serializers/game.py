"""
For ingesting the data from daily roll-up tarballs.
"""
from rest_framework import serializers

from apps.game_data.models import game as game_models
from apps.game_data.models import meta as meta_models
from apps.game_data.serializers.utils import JSONDashConvertMixin


class PlayerGameRecordSerializer(
    JSONDashConvertMixin,
    serializers.ModelSerializer
):
    """
    Processes JSON subfield containing a game "summary" for player.
    """

    player_id = serializers.CharField()

    def create(self, validated_data):
        validated_data['match'] = self.context['match']

        player_obj, _ = meta_models.SBBPlayer.objects.get_or_create(
            account_id=validated_data['player_id'])
        validated_data['player'] = player_obj
        del validated_data['player_id']

        return super().create(validated_data)

    class Meta:
        model = game_models.SBBGameParticipant
        fields = ('player_id',)


class GameTarSerializer(JSONDashConvertMixin, serializers.ModelSerializer):
    """
    Used to munch a json from one tarball file.
    """

    players = PlayerGameRecordSerializer(many=True)

    def create(self, validated_data):

        participants = validated_data.pop('players')
        game_obj = super().create(validated_data)
        self.fields['players'].context['match'] = game_obj
        self.fields['players'].create(participants)
        return game_obj

    class Meta:
        model = game_models.SBBGame
        fields = ('match_id', 'players')
        extra_kwargs = {'match_id': {'source': 'uuid'}}
