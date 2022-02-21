"""
Serializers for ingesting template id metadata.
"""
from rest_framework import serializers

from apps.game_data.models import meta as meta_models
from apps.game_data.serializers.utils import (
    ContextDefaulter,
    IDKeyListSerializer
)


class GamePieceSerializer(serializers.Serializer):
    """
    Class for ingesting json containing info on SBB game pieces:
    Treasures, Heroes, Characters, Spells.
    """

    # fields
    template_id = serializers.HiddenField(
        default=ContextDefaulter(source='key'))
    Id = serializers.CharField(source='slug')
    Name = serializers.CharField(max_length=32, source='name')

    mapping = {
        'TREASURE': meta_models.SBBTreasure,
        'SPELL': meta_models.SBBSpell,
        'HERO': meta_models.SBBHero,
        'CHARACTER': meta_models.SBBCharacter
    }

    def validate_Id(self, value):
        tokens = value.split('_')
        if not tokens[0] == 'SBB':
            raise serializers.ValidationError
        if tokens[1] not in self.mapping.keys():
            raise serializers.ValidationError

        if self.instance:
            model_cls = self.get_model(value)
            if not self.instance.__class__ == model_cls:
                raise serializers.ValidationError

        return value

    def create(self, validated_data):
        model_cls = self.get_model(validated_data['slug'])
        instance = model_cls._default_manager.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    def get_model(self, slug_value):
        """Return the type of model the slug corresponds to."""
        tokens = slug_value.split('_')
        return self.mapping[tokens[1]]

    class Meta:
        list_serializer_class = IDKeyListSerializer
