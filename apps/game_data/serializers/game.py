"""
For ingesting the data from daily roll-up tarballs.
"""
from rest_framework import serializers

from apps.game_data.models import game as game_models
from apps.game_data.serializers.participant_data import (
    PlayerGameRecordSerializer
)
from apps.game_data.serializers.utils import JSONDashConvertMixin


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
