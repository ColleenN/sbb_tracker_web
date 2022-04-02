from rest_framework import serializers

from apps.game_data.models import (
    game as game_models,
    meta as meta_models
)


class CombatMatchSerializer(serializers.Serializer):
    """
    Serializer for top-level json containing both player's data.
    """

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

    def save(self):

        if self.instance is None:

            round = self._context.get('round', None)
            acct_id = self._context.get('player_id', None)
            if round and acct_id:
                # TODO figure out how to work this into test setup
                game = self.parent.parent.parent.instance
                player_obj, _ = meta_models.SBBPlayer.objects.get_or_create(
                    account_id=acct_id)
                partic, _ = game_models.SBBGameParticipant.objects.get_or_create(
                    match=game, player_id=player_obj
                )
                self.instance, _ = game_models.SBBGameTurn.objects.get_or_create(
                    turn_num=round, participant=partic
                )

        return super().save()

    def update(self, instance, validated_data):

        characters = validated_data.pop('characters')
        char_serializer = self.fields.get('characters').child
        for item in characters:
            item['game_turn'] = self.instance
            in_db = game_models.SBBGameCharacter.objects.filter(
                game_turn=self.instance, position=item['position'])
            if in_db.exists():
                char_serializer.update(instance=in_db.get(), validated_data=item)
            else:
                char_serializer.create(validated_data=item)

        spells = validated_data.pop('spells')
        for index, item in enumerate(spells):
            in_db = game_models.SBBGameSpell.objects.filter(
                game_turn=self.instance, order=index)
            if in_db.exists():
                obj = in_db.get()
                obj.base_spell = item
                obj.save()
            else:
                game_models.SBBGameSpell.objects.create(
                    base_spell=item, order=index, game_turn=self.instance)

        return super().update(instance, validated_data)

    def create(self, validated_data):

        raise NotImplementedError()
