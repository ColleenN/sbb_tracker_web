from django.db import models

from apps.game_data.models import meta as metadata


class SBBGame(models.Model):
    """
    Describes one instance of an SBB game.
    NOT tied to a specific player's POV!
    """

    uuid = models.UUIDField(unique=True)

    # Ask isik - can we get client patch stamp?


class SBBGameParticipant(models.Model):
    """
    Refers to a player 'in-lobby' for a specified game.
    """

    match = models.ForeignKey(SBBGame, on_delete=models.DO_NOTHING)
    player = models.ForeignKey(metadata.SBBPlayer, on_delete=models.DO_NOTHING)


