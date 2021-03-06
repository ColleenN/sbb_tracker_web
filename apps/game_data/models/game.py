from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.game_data.models import meta as metadata


class SBBGame(models.Model):
    """
    Describes one instance of an SBB game.
    NOT tied to a specific player's POV!
    """

    uuid = models.UUIDField(unique=True)
    player_list = models.ManyToManyField(
        metadata.SBBPlayer,
        through='SBBGameParticipant',
        through_fields=('match', 'player')
    )

    # Ask isik - can we get client patch stamp?


class SBBGameParticipant(models.Model):
    """
    Refers to a player 'in-lobby' for a specified game.
    """

    match = models.ForeignKey(SBBGame, on_delete=models.CASCADE)
    player = models.ForeignKey(metadata.SBBPlayer, on_delete=models.PROTECT)
    placement = models.IntegerField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='place_min', check=models.Q(placement__gte=1)),
            models.CheckConstraint(
                name='place_max', check=models.Q(placement__lte=8))
        ]


class SBBGameTurn(models.Model):
    """
    Record of each player's turn.
    """

    turn_num = models.IntegerField(validators=(MinValueValidator(1),))
    participant = models.ForeignKey(
        SBBGameParticipant, on_delete=models.CASCADE)
    hero = models.ForeignKey(
        metadata.SBBHero, null=True, on_delete=models.PROTECT)
    hp = models.IntegerField(null=True)
    level = models.IntegerField(null=True)
    exp = models.IntegerField(null=True)
    treasures = models.ManyToManyField(metadata.SBBTreasure)
    characters = models.ManyToManyField(
        metadata.SBBCharacter,
        through='SBBGameCharacter',
        through_fields=('game_turn', 'base_character')
    )
    spells = models.ManyToManyField(
        metadata.SBBSpell,
        through='SBBGameSpell',
        through_fields=('game_turn', 'base_spell')
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='exp_floor', check=models.Q(exp__gte=0)),
            models.CheckConstraint(
                name='exp_cap', check=models.Q(exp__lt=3))
        ]


class SBBGameCharacter(models.Model):
    """
    A character as it exists on a player's board/hand
    as they finish their shopping for the turn.
    """

    base_character = models.ForeignKey(
        metadata.SBBCharacter, on_delete=models.PROTECT)
    game_turn = models.ForeignKey(SBBGameTurn, on_delete=models.PROTECT)
    attack = models.IntegerField()
    health = models.IntegerField()
    golden = models.BooleanField()
    position = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(7)
        )
    )


class SBBGameSpell(models.Model):

    base_spell = models.ForeignKey(
        metadata.SBBSpell, on_delete=models.PROTECT)
    game_turn = models.ForeignKey(SBBGameTurn, on_delete=models.CASCADE)
    order = models.IntegerField()
