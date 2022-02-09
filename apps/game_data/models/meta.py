"""
For data that isn't expected to regularly change within the course of a single game.
"""
from django.db import models


class SBBPlayer(models.Model):
    """
    Corresponds one player account within SBB game.
    """


class SBBHero(models.Model):
    """
    A Hero within SBB.
    """


class SBBCharacter(models.Model):
    """
    A character within SBB.
    """
