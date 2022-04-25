"""
For data that isn't expected to regularly change within the course of a single game.
"""
from django.db import models


class SBBPlayer(models.Model):
    """
    Corresponds one player account within SBB game.
    """
    account_id = models.CharField(unique=True, max_length=128)
    possibly_mythic = models.BooleanField(null=True, default=None)


class SBBGamePiece(models.Model):
    """
    An SBB Game Piece described by a single template id.
    """
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=128)
    template_id = models.IntegerField()

    class Meta:
        abstract = True


class SBBHero(SBBGamePiece):
    """A Hero within SBB."""


class SBBCharacter(SBBGamePiece):
    """A character within SBB."""


class SBBTreasure(SBBGamePiece):
    """A Treasure in SBB."""


class SBBSpell(SBBGamePiece):
    """A spell in SBB."""

