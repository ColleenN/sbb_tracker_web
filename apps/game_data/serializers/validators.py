"""
Custom validators for our serializers.
"""
from rest_framework.serializers import ValidationError


class XPStringValidator:
    """
    We're going to check that string describes a valid XP value, meaning:
    1. Its of the format <X>.<Y>
    2. The 1st value is an integer
    3. The 2nd value is a 0, 1 or 2.
    """

    def __call__(self, value):

        level, fraction = value.split('.')
        try:
            int(level)
        except ValueError:
            raise ValidationError(f'Level token {level} not an integer.')

        if fraction not in ['0', '1', '2']:
            raise ValidationError(
                f'XP fraction token {fraction} not a valid partial XP value.')

        return value


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
