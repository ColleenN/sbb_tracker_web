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
    placement = serializers.IntegerField(min_value=1, max_value=8)
    player_id = serializers.CharField()

    def update(self, instance, validated_data):
        """
        Update an existing SBBGame.
        Will usually be a JSON from a different player's perspective.
        """
        validated_data.pop('players')
        placement = validated_data.pop('placement')
        main_player_id = validated_data.pop('player_id')
        participant_objs = instance.sbbgameparticipant_set.all()

        for participant in participant_objs:
            if participant.player.account_id == main_player_id:
                participant.placement = placement
                participant.save()

        return instance

    def create(self, validated_data):
        """Create a whole new SBBGame from scratch."""
        participants = validated_data.pop('players')
        placement = validated_data.pop('placement')
        main_player_id = validated_data.pop('player_id')

        game_obj = super().create(validated_data)
        self.fields['players'].context['match'] = game_obj
        participant_objs = self.fields['players'].create(participants)

        for participant in participant_objs:
            if participant.player.account_id == main_player_id:
                participant.placement = placement
                participant.save()

        return game_obj

    class Meta:
        model = game_models.SBBGame
        fields = ('match_id', 'players', 'placement', 'player_id')
        extra_kwargs = {'match_id': {'source': 'uuid'}}
