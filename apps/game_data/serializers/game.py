"""
For ingesting the data from daily roll-up tarballs.
"""
from rest_framework import serializers
from apps.game_data.models import game as game_models


class GameTarSerializer(serializers.ModelSerializer):
    """
    Used to munch a json from one tarball file.
    """

    def save(self, **kwargs):
        pass

    class Meta:

        model = game_models.SBBGame
        fields = ('match-id', 'player-id')
        extra_kwargs = {'match-id': {'source': 'match_uuid'}}


class PlayerGameRecordSerializer(serializers.ModelSerializer):
    """
    Processes JSON subfield containing a game "summary" for player.
    """

    class Meta:
        model = game_models
