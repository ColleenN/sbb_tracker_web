"""
For ingesting the data from daily roll-up tarballs.
"""
from rest_framework import serializers

from apps.game_data.models import game as game_models
from apps.game_data.models import meta as meta_models
from apps.game_data.serializers.participant_data import (
    PlayerGameRecordSerializer
)
from apps.game_data.serializers.combat_data import CombatMatchSerializer
from apps.game_data.serializers.utils import JSONDashConvertMixin


class GameTarSerializer(JSONDashConvertMixin, serializers.ModelSerializer):
    """
    Used to munch a json from one tarball file.
    """

    players = PlayerGameRecordSerializer(many=True)
    placement = serializers.IntegerField(min_value=1, max_value=8)
    player_id = serializers.CharField()
    combat_info = CombatMatchSerializer(many=True)
    match_id = serializers.UUIDField(source='uuid')

    def update(self, instance, validated_data):
        """
        Update an existing SBBGame.
        Will usually be a JSON from a different player's perspective.
        """
        participants = validated_data.pop('players')
        placement = validated_data.pop('placement')
        main_player_id = validated_data.pop('player_id')

        for participant in participants:
            if participant['player_id'] == main_player_id:
                participant['placement'] = placement

        self.update_participants(instance, new_participants=participants)

        return instance

    def validate_players(self, value):
        """Check that we aren't about to end up with 9+ participants."""
        return value

    def update_participants(self, instance, new_participants):

        existing = instance.sbbgameparticipant_set.values_list(
            'player__account_id', flat=True)
        for item in new_participants:
            item['match'] = instance
            if item['player_id'] not in existing:
                self.fields.get('players').child.create(item)
            else:
                self.fields.get('players').child.update(
                    validated_data=item,
                    instance=game_models.SBBGameParticipant.objects.get(
                        player__account_id=item['player_id'],
                        match=instance
                    )
                )

    def create(self, validated_data):
        """Create a whole new SBBGame from scratch."""

        self.instance, _ = game_models.SBBGame.objects.get_or_create(
            uuid=self.validated_data['uuid'])
        return self.update(self.instance, validated_data)

    class Meta:
        model = game_models.SBBGame
        fields = ('match_id', 'players', 'placement', 'player_id', 'combat_info')
