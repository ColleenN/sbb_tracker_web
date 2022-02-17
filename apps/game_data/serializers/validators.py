"""
Custom validators for our serializers.
"""
from rest_framework.serializers import ValidationError


class ValidateRootJSONPlayer:
    """
    Verifies that the player id in the root level of our JSON shows up in the
    player list of the match-level data.

    Intended only for use on GameTarSerializer.
    """
    requires_context = True

    def __call__(self, attrs, serializer_field):

        # Expect this to be a PlayerGameRecordSerializer
        players = attrs['player-id']
        if players.is_valid():
            id_list = map(lambda x: x['player-id'], players.validated_data)
            if attrs['player-id'] not in id_list:
                raise ValidationError(
                    "Player is not listed as match participant.")
        else:
            raise ValidationError(
                "Can't verify player is participant in match.")
