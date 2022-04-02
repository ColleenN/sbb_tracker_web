from rest_framework import serializers

from apps.game_data.models import (
    game as game_models,
    meta as meta_models
)
from apps.game_data.serializers.utils import ContextDefaulter


class GameCharacterSerializer(serializers.ModelSerializer):

    id = serializers.SlugRelatedField(
        slug_field='template_id',
        queryset=meta_models.SBBCharacter.objects.all(),
        source='base_character'
    )

    class Meta:
        model = game_models.SBBGameCharacter
        fields = ('id', 'attack', 'health', 'golden', 'position')

    def to_internal_value(self, data):

        # Forcibly validate golden field first, so we can massage id
        # if it is in fact an upgraded unit.
        gold_field = self.fields.get('golden')
        primitive_value = gold_field.get_value(data)
        golden_validated = gold_field.run_validation(primitive_value)
        if golden_validated:
            data['id'] = str(int(data['id'])-1)

        return super().to_internal_value(data)


class CombatSerializer(serializers.ModelSerializer):
    """
    For info on one round of combat from one player's POV.
    """

    round = serializers.HiddenField(default=ContextDefaulter(source='round'))
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
        fields = ('characters', 'spells', 'treasures', 'round')

    def update(self, instance, validated_data):

        characters = validated_data.pop('characters', None)
        if characters:
            instance.characters.clear()
        char_serializer = self.fields.get('characters').child
        for item in characters:
            item['game_turn'] = self.instance
            char_serializer.create(validated_data=item)

        spells = validated_data.pop('spells', None)
        if spells:
            instance.spells.clear()
        for index, item in enumerate(spells):
            game_models.SBBGameSpell.objects.create(
                    base_spell=item, order=index, game_turn=self.instance)

        if validated_data.get('treasures', None):
            instance.treasures.clear()

        return super().update(instance, validated_data)

    def create(self, validated_data):

        round = validated_data.get('round')
        participant = validated_data.get('participant')
        self.instance, _ = game_models.SBBGameTurn.objects.get_or_create(
                turn_num=round, participant=participant)
        return self.update(self.instance, validated_data)


class CombatMatchSerializer(serializers.Serializer):
    """
    Serializer for top-level json containing both player's data.
    """

    main_player = CombatSerializer()
    opponent = CombatSerializer()

    def to_internal_value(self, data):
        main_player = self.parent.initial_data['player-id']
        data['main_player'] = data.pop(main_player)
        self.fields.get('main_player').context['player_id'] = main_player
        self.fields.get('main_player').context['round'] = data['round']

        known_keys = {'round', 'sim-results', 'main_player'}
        leftover_keys = set(data.keys()) - known_keys
        op_id = leftover_keys.pop()
        data['opponent'] = data.pop(op_id)
        self.fields.get('opponent').context['player_id'] = op_id
        self.fields.get('opponent').context['round'] = data['round']

        return super().to_internal_value(data)

    def create(self, validated_data):
        game = self.parent.instance

        main_p_field = self.fields.get('main_player')
        acct_id = main_p_field.context['player_id']
        player_obj, _ = meta_models.SBBPlayer.objects.get_or_create(
            account_id=acct_id)
        participant, _ = game_models.SBBGameParticipant.objects.get_or_create(
            match=game, player_id=player_obj)
        main_p_data = validated_data.get('main_player')
        main_p_data['participant'] = participant
        main_p_turn = main_p_field.create(main_p_data)

        op_field = self.fields.get('opponent')
        acct_id = op_field.context['player_id']
        player_obj, _ = meta_models.SBBPlayer.objects.get_or_create(
            account_id=acct_id)
        participant, _ = game_models.SBBGameParticipant.objects.get_or_create(
            match=game, player_id=player_obj)
        op_data = validated_data.get('opponent')
        op_data['participant'] = participant
        op_turn = op_field.create(validated_data.get('opponent'))

        return [main_p_turn, op_turn]
